# Archim2 Driver Option

The Archim2 is a popular open-source hardware driver for a 3D printer. The ChipShover can also be built using this board, although it has some limitations and is **not supported in any official manner**, but instead presented as a community build information.


## Limitations

Archim2 uses the less powerful TMC2130 (1.2A RMS coil current, vs 2.0A RMS coil current on TMC2660 used in ChipShover-One). The primary effect of this is that microstepping may be more likely to lose steps, so a smaller default microstepping value is used.

## Build List

### Archim2 Driver Option

* [Archim2 with Optical End-Stops](https://ultimachine.com/products/archim2). You won't use the end stops, but need the connectors from it.
* 3x Small Heatsinks (see note below).
* 1x 24V, 40mm fan, 2-lead input.
* 1x 3D Printed fan holder
* 2x M4 screws (for fan)
* 2x 4-40 or M3 screws (for fan holder)

#### Heatsinks

Driving the motors *will* require a heatsink on the Archim2. The easiest solution is to buy the widely available "Raspberry Pi Heatsink Pack", such as [FIT0542](https://www.digikey.com/en/products/detail/dfrobot/FIT0542/8549500) for less than $2.

You'll only need the *smallest* heatsink from each pack, so buy 3 packs as you need heatsinks on each X/Y/Z.

#### 24V Fan

The heatsink alone might not be enough, so also plan on getting a 24V fan. We'll use the built-in support for driving a fan (designed for use with the 'extruders').

#### Driver Cables

You'll also need the driver cables for your motor.