# Stepper Controllers

## ChipShover-One

ChipShover-One is NewAE Technology Inc's premium control box. When people come into your lab, they will know you mean serious business. We've done foolish things like using a [$75 joystick part](https://www.digikey.com/en/products/detail/nidec-copal-electronics/CJ25-82010/5042406), which cost more than the entire cost of other lower-cost solutions.

But it's not just silly choices that make this useful - with ChipShover-One you get capabilities like:

* Feedback connections to allow probing to detect collisions with target device and stop movement.
* Physical jog stick for X/Y/Z.
* Physical pause/stop button to abort moves without losing motor power.
* E-Stop button to abort moves & kill motor power.
* Colour TFT Display for feedback on position, motor driver status, etc.
* Python 3 API Interface for usage in Jupyter notebooks.
* Compact desktop size.

Beneath the hood, we're worked hard to give you a lot of flexibility that you won't find in proprietary solutions:

* Arduino Due (SAM3X8E) based controller running Marlin2 firmware.
* TMC2660 Based 2-phase Stepper Drivers
* RS485 + I2C + GPIO Extension connectors *per channel*.

This allows implementation of additional features, such as adding a "crash detection" probe. This allows the controller to automatically abort a movement if it detects it will hit the probe surface (**NB: this feature requires you to implement it currently**).

### ChipShover-One Controller Kit

* ChipShover-One in Aluminum Enclosure
	* 3x 2-Phase Stepper driver board (CW562) installed
	* 1x 2-Phase Stepper driver board (CW562) spare
* 90W power supply (24V / 3.75A) with US + EU plugs included
* 3x 1m stepper motor cables
* 3x stepper motor breakout boards (for connecting tables besides the NewAE one)
* 1x stepper motor diagnostic board (allows scoping signals)
* 3x extension cable breakout connectors
* 2x spare fuses
* 1x USB 2.0 cable


## ChipShover-Three-Quarters

ChipShover-Three-Quarters is a variant of ChipShover-One for people who want a lower-cost option. In order to reduce the cost, this solution does not come with the milled aluminum enclosure, and instead comes with a simple laser-cut enclosure.

* E-Stop switch.
* Push-button jog board.
* Controller boards do not have extension parts mounted.

The ChipShover-3Q mainboard is identical to the ChipShover-One, so the same firmware features can be used on either board.