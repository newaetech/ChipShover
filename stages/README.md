# XYZ Stages

The mechanical part of the XYZ table is actually the "most boring", because it's well known. XYZ stages are found in applications such as:

* Microscopes
* CNC
* Engravers
* 3D printers

The most accurate system will use some sort of feedback - the most basic would be on the shaft itself (to detect how far we are rotating the leadscrew), the more accurate would be to have real-time information on the position of the table. With closed loop feedback we can achieve very high levels of repeatability.

Currently *all* of the stages we discuss are open-loop, where we use stepper motors in a direct-drive fashion. Achieving a higher resolution is done with a finer leadscrew. You can also gear down the motors to improve resolution, which has some impact on backlash (not an issue if closed-loop, but is an issue if open-loop).

## Stage Calibration

In order to better characterize our stage setup, we set up a laser interferometer. This allows us to achieve very high resolution measurements, which are highly stable and thus can answer questions such as how repeatable a given stage is when moving back and forth many times.

We are using the setup that [Sam Zeloof describes](https://www.youtube.com/watch?v=vPu6lN9yJOY), which can be assembled for much less than an off the shelf unit.