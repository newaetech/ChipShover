# /*******************************************************************************
# * File Name: cs.py
# *
# * Description:
# * The Python API for the ChipShover.
# * 
# * 
# ********************************************************************************
# * Copyright 2021 NewAE Technology Inc.
# * SPDX-License-Identifier: Apache-2.0
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *     http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# ********************************************************************************/
'''
    ChipShover API Documentation
    ============================

    For typical usage, after starting the ChipShover, you should 
    first home the stepper motors. This serves as a calibration step:

    Example
    -------

    >>> from chipshover import ChipShover
    >>> shv = ChipShover('COM5')
    >>> shv.home()

    From there, you can use the API to set the ChipShover's position:

    >>> shv.move(10, 20, 190) # x=10, y=20, z=190

    Note that the Z-axis default position is typically 200 to start with.

    The ChipShover can also be swept along the XY axis:

    >>> for x,y in shv.sweep_x_y(0, 5, 0, 5, step=0.5):
            print("at %f, %f"%(x, y))

    While using the ChipShover, it may become necessary to pause
    or stop the ChipShover. This can be done by either the stop
    or kill command. With the former, the ChipShover can
    continue on as usual after the stoppage; however, the latter
    will stop the ChipShover until it is power cycled.

    >>> shv.stop() # can continue on from here with new movement commands
    >>> shv.kill() # require a power cycle to continue operation

    Note that if a stop command is used, the ChipShover's measured position
    may become incorrect. As such, it is recommended that a homing
    command be performed after a stop is issued. In practice, the position
    seems to still be fairly accurate after a stop and so this is only
    recommended and not required.
    
    If using most commands interactively (from a Jupyter notebook),
    hitting Ctrl-C should issue a `stop()` command. The assumption is if you
    interrupt the program with Ctrl-C that is because bad things were about to
    happen. Without the `stop()` command, the controller will finish
    executing the last command, such as a move.

'''
import serial
import time
from .samba import Samba
import os
import base64
import datetime
import binascii


def firmware_update(comport, fw_path=None):
    """ Flashes new firmware to the SAM3X8E (this command is for ChipShover-One only).

    Args:
        comport (str): Path to serial port, ex COM4
        fw_path (str): Path to binary firmware file. If None, flash using default firmware
                        Defautls to None.
    """
    sam = Samba()
    try:
        sam.con(comport)
        print("Connected")
        sam.erase()
        print("Erased")
        if fw_path:
            fw_data = open(fw_path, "rb").read()
        else:
            from .firmware import getsome
            fw_data = getsome('firmware.bin').read()

        sam.write(fw_data)
        print("Written")

        if sam.verify(fw_data):
            sam.flash.setBootFlash(True)
            print("Setting boot from flash")
            sam.ser.close()
            print("Firmware update succeeded: PLEASE POWER CYCLE CHIPSHOVER")
        else:
            sam.ser.close()
            raise OSError("Firmware verify FAILED!")
    except:
        sam.ser.close()
        raise

def _gen_firmware(fw_path=None):
    f = open("firmware.py", "w")

    f.write("# This file was auto-generated. Do not manually edit or save. What are you doing looking at it? Close it now!\n")
    f.write("# Generated on %s\n"%datetime.datetime.now())
    f.write("#\n")
    f.write("import binascii\n")
    f.write("import io\n\n")
    f.write("fwver = [%d, %d]\n" % (0, 1))
    f.write("def getsome(item, filelike=True):\n")
    f.write("    data = _contents[item].encode('latin-1')\n")
    f.write("    data = binascii.a2b_base64(data)\n")
    f.write("    if filelike:\n")
    f.write("        data = io.BytesIO(data)\n")
    f.write("    return data\n\n")
    f.write("_contents = {\n")

    f.write("")
    if fw_path is None:
        fw_path = '../../../ChipSHOVER-Marlin/.pio/build/DUE_chipshover/firmware.bin'

    with open(fw_path, "rb") as e_file:
        # json_str = base64.b64encode(e_file.read())# json.dumps(e_file.read(), ensure_ascii=False)
        json_str = binascii.b2a_base64(e_file.read())

        f.write("\n#Contents from %s\n"%fw_path)
        f.write("'%s':'"%'firmware.bin')
        f.write(json_str.decode().replace("\n",""))
        f.write("',\n\n")
        f.flush()
    f.write("}\n")
    pass

class ChipShover:
    """ChipShover is a controller for XYZ tables. Assumes Marlin-based
       firmware for commands.
       
       
    """
    
    #Default ChipShover table/firmware combo
    STEPS_PER_MM = 1600
    
    def __init__(self, comport):
        """Connect to ChipShover-Controller using given serial port."""
        self.ser = serial.Serial(comport, rtscts=True)
        self._com = comport
        
        #Required for ChipShover-One + Archim2 USB serial
        self.ser.rtscts = True
        self.ser.timeout = 0.25
        self.z_home = None

        self.ser.flush()
        self.ser.reset_input_buffer()
        
        #Check if table seems legit
        
        #Abs mode by default
        self.ser.write(b"G90\n")
        self.wait_done()
        
        #MM by default
        self.ser.write(b"G21\n")
        self.wait_done()

        #Check the "steps per unit" is valid
        self.ser.write(b"M503\n")
        results = self.wait_done()
        try:
            splitres = results.split(b"Steps per unit:\necho: M92")[1].split(b"\n")[0]
            splitres = splitres.split(b" ")
            if splitres[1][0] != ord('X') or \
               splitres[2][0] != ord('Y') or \
               splitres[3][0] != ord('Z'):
                raise IOError("Communication problem attempting to read" + \
                               "M503 response. %s was splitres"%splitres)
            xsteps = float(splitres[1][1:])
            ysteps = float(splitres[2][1:])
            zsteps = float(splitres[3][1:])

            if xsteps != ysteps != zsteps:
                raise ValueError("XSTEPS/YSTEPS/ZSTEPS differs. Abort. %f %f %f"%(xsteps, ysteps, zsteps))

            if xsteps < 100 or xsteps > 10E3:
                raise ValueError("Sanity check in XSTEPS failed. %f"%xsteps)

            self.STEPS_PER_MM = int(xsteps)

        except:
            print("Failed to read steps/mm, check communication is OK.")
            print("Response to M503: %s"%results)
            raise


        self.set_fan(50)

        self.call_stop_on_ctrlc = True
        
        #TODO - 
        #signal.signal(signal.SIGINT, self.stop)
        
    def set_fan(self, fan_speed=100):
        """Sets cooling fan speed, range of 0 - 100"""

        fan_pwm = (float(fan_speed) / 100.0)*255
        fan_pwm = int(round(fan_pwm))
        fan_pwm = min(fan_pwm, 255)
        fan_pwm = max(fan_pwm, 0)

        #Early protos had this as P1, now P0
        self.ser.write(b"M106 P0 S%d\n"%fan_pwm)
        self.wait_done()

    def close(self):
        """Closes serial port"""
        self.set_fan(0)
        self.ser.close()
        
    def stop(self):
        """Calls EMERGENCY STOP command (M410).
        
        Stops movement, but allows further commands. Sending this will
        cause positionvto be wrong if table was moving at the time."""
        self.ser.write(b"M410\n")
        print("**STOP CALLED. Motor positions will be incorrect. Please re-home.")
        self.wait_done()
        
    def kill(self):
        """Calls KILL command (M112) to stop all movement.
        
        This will stop all table movement and shut down the
        controller, requiring a power cycle to recover. Useful
        when you have a serious error condition you want to
        ensure someone physically clears.
        """
        self.ser.write(b"M112\n")
        print("***KILL CALLED. Power Cycle Needed!***")
        self.wait_done()
        
    def move_zdepth(self, z_depth):
        """Sets the Z axis to a given 'depth', as referenced from home.
        
        The default Z-Axis homing sets the Z axis to some positive value, with
        Z = 0 being the axis bottom. Most of the time you'd like to specify depth
        below home position instead, this function lets you do that.
        """
        
        if self.z_home is None:
            raise ValueError("Run Homing First")
        self.move(z= self.z_home - z_depth)
        
    def move(self, x=None, y=None, z=None, debug=False):
        """Move table to commanded X, Y, Z location.
        
        Uses a `G0` command to move the table. The function
        will use a `M400` command to wait for the movement
        to complete before returning.
        
        WARNING: The `z` is an absolute position - the default
                 home `z` is often the MAXIMUM value. Thus a
                 move to z=0` may slam your table into the ground.
                 You can use the `move_zdepth()` function for
                 moving a depth from the home position instead.
        """
        
        cmdstr = b"G0 "
        if x is not None:
            cmdstr += b"X%f"%x
        if y is not None:
            cmdstr += b"Y%f"%y
        if z is not None:
            cmdstr += b"Z%f"%z
            
        cmdstr += b"\n"
        
        if debug:
            print(cmdstr)
            
        
        self.ser.write(cmdstr)        
        self.wait_done()

        self.wait_for_move()
        
    def wait_for_move(self):
        """Wait for current movement to be done"""

        self.ser.flush()
        self.ser.reset_input_buffer()
        #wait for move to finish
        self.ser.write(b"M400\n")
        self.wait_done()


    def get_position(self, forcefinish=True):
        """Gets the X/Y/Z position of the table.
        
        By default will wait for any movement to
        finish, as reading position during movement
        will return incorrect (final not current)
        position.
        """
        
        if forcefinish:
            #wait for move to finish
            self.wait_for_move()
        
        self.ser.write(b"M114\n")
        
        pos_line = self.ser.readline()
        ok = self.ser.readline()
        
        if ok != b'ok\n':
            print("DEBUG: 'pos_line': %s"%pos_line)
            print("DEBUG: 'ok' line : %s"%ok)
            raise IOError("Com error on M114 - received %s, expected 'ok'\n"%ok)
            
        
        pos_line = pos_line.split(b' ')       
        if (pos_line[0][0] != ord('X')) or \
           (pos_line[1][0] != ord('Y')) or \
           (pos_line[2][0] != ord('Z')) or \
           (pos_line[5][0] != ord('X')) or \
           (pos_line[6][0] != ord('Y')) or \
           (pos_line[7][0] != ord('Z')):
                raise IOError("Unknown position format: %s"%pos_line)

                
        x_mm = float(pos_line[0][2:])
        y_mm = float(pos_line[1][2:])
        z_mm = float(pos_line[2][2:])
 
        x_cnt = float(pos_line[5][2:])
        y_cnt = float(pos_line[6][2:])
        z_cnt = float(pos_line[7][2:])
        
        #Count values are more accurate
        
        calc_x_mm = x_cnt * (1.0/float(self.STEPS_PER_MM))
        calc_y_mm = y_cnt * (1.0/float(self.STEPS_PER_MM))
        calc_z_mm = z_cnt * (1.0/float(self.STEPS_PER_MM))
        
        if round(calc_x_mm, 2) != x_mm:
            raise IOError("Reporting error: %f != %f (based on count of %d)"%(x_mm, calc_x_mm, x_cnt))

        if round(calc_y_mm, 2) != y_mm:
            raise IOError("Reporting error: %f != %f (based on count of %d)"%(y_mm, calc_y_mm, y_cnt))
            
        if round(calc_z_mm, 2) != z_mm:
            raise IOError("Reporting error: %f != %f (based on count of %d)"%(z_mm, calc_z_mm, z_cnt))
            
        return calc_x_mm, calc_y_mm, calc_z_mm
        
    def home(self, x=True, y=True, z=True):
        """Perform homing operation using G28 command.
        
        Calling this will home the X, Y, and Z axis (you can
        disable specific axis as well). The command will block
        until the homing operation is complete.
        """

        self.ser.flush()
        self.ser.reset_input_buffer()        
        
        if x == y == z == False:
            return
        
        self.ser.write(b"G28")
        if x:
            self.ser.write(b" X")
        if y:
            self.ser.write(b" Y")
        if z:
            self.ser.write(b" Z")
        self.ser.write(b"\n")
        
        home_resp = self.wait_done()
        
        self.z_home = self.get_position()[2]
        
        return home_resp

    def sweep_x_y(self, x_start, x_end, y_start, y_end, step=0.1, x_step=None, y_step=None, z_plunge=0):
        """Sweep X-Y range, yielding at each point.
        
        This function should be used in a simple sweep, for example:

            for x,y in cs.sweep_x_y(0, 5, 0, 5, step=0.5):
                print("At %f, %f"%(x,y))

        If you call your fault injection probe to active at the point, you will
        get a simple fault injection performed over a linear X-Y range.

        The `z_plunge` parameter can be used to specify a certain amount of z-plunge
        performed at each point. This is normally used with BBI or similar probes that
        must be put in contact with the die.
        
        If using interactive Python (Jupyter), hitting `Ctrl-C` during this
        function run will call `stop()` by default.
        """

        if x_start > x_end:
            raise ValueError("X End must be numerically larger than X Start")

        if y_start > y_end:
            raise ValueError("Y End must be numerically larger than Y Start")

        if x_step is None:
            x_step = step

        if y_step is None:
            y_step = step

        x = x_start      

        while x <= x_end:
            self.move(x=x)
            y = y_start
            while y <= y_end:
                self.move(y=y)         

                if z_plunge:
                    old_z = self.get_position()[2]
                    self.move(z = (old_z-z_plunge))

                yield (x, y)

                if z_plunge:
                    self.move(z = old_z)

                y += y_step
            x += x_step



    def wait_done(self, timeout=5, debug=False):
        """Wait for a command to be acknowledged by checking for 'ok' response.
        
        Some G commands return immediatly, for example G0 returns an 'ok' and
        does not wait for the command to execute. Others will block until the
        command finishes executing, for example the homing operation (G28) 
        does not return 'ok' until it is done.
        
        By default if a `KeyboardInterrupt` is detected (from a Ctrl-C operation)
        then stop() will be called. This is done in case you are using
        ChipShover interactively and hit Ctrl-C to try and abort a move operation.
        """
        
        try:
            timeout = timeout * 4
            timeout_cnt = 0

            debug_data = b""
            while True:                
                resp = self.ser.readline()

                if resp:
                    debug_data += resp

                if resp and debug:
                    print(resp)

                #This is an OK response - indicates device is alive
                if resp == b'echo:busy: processing\n':
                    timeout_cnt = 0

                #Done deal I guess
                if resp == b'ok\n':
                    break

                time.sleep(0.25)
                timeout_cnt += 1

                if timeout_cnt > timeout:
                    raise IOError("Device timed out, responses: %s"%str(debug_data))

        except KeyboardInterrupt:
            if self.call_stop_on_ctrlc:
                print("Ctrl-C detected - calling stop() to stop table movement")
                self.stop()
            raise
        
        #Sometimes buffer seems to have stuff in it still - do one last read
        resp = self.ser.readline()
        debug_data += resp
        
        return debug_data

    def status(self):
        """ Gets the status of the ChipShouter

        This function CANNOT tell whether a fuse
        or emergency stop event has happened.

        Statuses:
            1. Idle
            2. Unhomed
            3. 5V fuse blown
        """
        self.ser.write(b"M14400\n")
        pos_line = self.ser.readline()
        if not pos_line:
            return None
        if (pos_line[0] == 0):
            return "Idle"
        elif (pos_line[0] == 2):
            return "Unhomed"
        elif (pos_line[0] == 8):
            return "5V fuse blown"
        #ok = self.ser.readline()

    def erase_firmware(self):
        """Erases the firmware of the SAM3X on the ChipShover

        Reprogram with::

            from chipshover import update_firmware
            firmware_update("comport")
        """
        self.ser.write(b"M997\n")

    def auto_program(self, fw_path=None):
        """Erase and reprogram the chipshover

        Args:
            fw_path (str): Path to firmware. If none, use default firmware.
                            Defaults to None.

        If com port detection fails, reprogramming must be done with firmware_update()
        """
        import time, serial.tools.list_ports
        before = serial.tools.list_ports.comports()
        before = [b.device for b in before]
        time.sleep(0.5)
        self.ser.write(b"M997\n")
        time.sleep(5.5)
        after = serial.tools.list_ports.comports()
        after = [a.device for a in after]
        candidate = list(set(before) ^ set(after) ^ set([self._com]))
        # print(candidate)
        # print(before, after, self._com)
        if len(candidate) == 0:
            raise OSError("Could not detect COMPORT. Continue using programmer.program()")
        com = candidate[0]
        print("Detected com port {}".format(com))
        firmware_update(com, fw_path)
