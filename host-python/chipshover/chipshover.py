import serial
import time
#import signal

class ChipShover(object):
    """ChipShover is a controller for XY(Z) tables. Assumes Marlin-based
       firmware for most commands."""
    
    STEPS_PER_MM = 1600
    
    def __init__(self, comport):
        """Connect to ChipShover-Controller using given serial port."""
        self.ser = serial.Serial(comport)
        
        #Required for Archim2 USB serial
        self.ser.rtscts = True
        self.ser.timeout = 0.25
        self.z_home = None
        
        #Check if table seems legit
        
        #Abs mode by default
        self.ser.write("G90\n")
        self.wait_done()
        
        #MM by default
        self.ser.write("G21\n")
        self.wait_done()
        
        #TODO - 
        #signal.signal(signal.SIGINT, self.stop)
        
    def close(self:
        """Closes serial port"""
        self.ser.close()
        
    def stop(self):
        """Calls EMERGENCY STOP command (M410).
        
        Stops movement, but allows further commands. Sending this will
        cause positionvto be wrong if table was moving at the time."""
        self.ser.write(b"M410\n")
        prtin("**STOP CALLED. Motor positions will be incorrect. Please re-home.")
        
    def kill(self):
        """Calls KILL command (M112) to stop all movement.
        
        This will stop all table movement and shut down the
        controller, requiring a power cycle to recover. Useful
        when you have a serious error condition you want to
        ensure someone physically clears.
        """
        self.ser.write(b"M112\n")
        print("***KILL CALLED. Power Cycle Needed!***")
        
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
        """
        
        cmdstr = b"G0 "
        if x:
            cmdstr += b"X%f"%x
        if y:
            cmdstr += b"Y%f"%y
        if z:
            cmdstr += b"Z%f"%z
            
        cmdstr += b"\n"
        
        if debug:
            print(cmdstr)
            
        self.ser.write(cmdstr)
        
        self.wait_done()
        
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
            self.ser.write(b"M400\n")
        self.wait_done()
        
        self.ser.write(b"M114\n")
        
        pos_line = self.ser.readline()
        ok = self.ser.readline()
        
        if ok != b'ok\n':
            raise IOError("Com error on M114\n")
            
        
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
    
    def wait_done(self, timeout=5, debug=False, kill_on_ctrlc=True):
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

            while True:
                debug_data = b""
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
            if kill_on_ctrlc:
                print("Ctrl-C detected - calling stop() to stop table movement")
                self.stop()
            raise
                    
        return debug_data