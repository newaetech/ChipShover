# ChipShover®

ChipShover is an XYZ table &amp; driver, with handy Python interface. It's designed for close analysis of ICs using tools like Electromagnetic Fault Injection (EMFI), EM Probes for side-channel, and more. In both specifications and cost it falls somewhere between between 3D printers & microscope stages.

## Python Interface

A Python interface simplifies use from existing Jupyter notebooks and similar.

Here is an example usage to sweep an IC surface from (10.0, 10.0) to (12.5, 12.5) in 0.05mm steps. Also plunge the Z-axis down to touch a probe to the surface at each location (useful when probe cannot be dragged across surface safely).

	from chipshover import ChipShover

	shv = ChipShover('com3')

	shv.home()

	for x,y in shv.sweep_x_y(10, 12.5, 10, 12.5, step=0.05, z_plunge=1.5):
	    print("At %f, %f"%(x,y))

## Installing ChipShover Python

Install `chipshover` like any other Python package. It should be available on [pypi.org](https://pypi.org/project/chipshover/) so you can do:

	pip install chipshover

## Full Python Documentation

See [chipshover.readthedocs.io](http://chipshover.readthedocs.io/) for the full API documentaiton (auto-built from Python).