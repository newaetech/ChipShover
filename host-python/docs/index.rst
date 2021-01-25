.. ChipSHOVER documentation master file, created by
   sphinx-quickstart on Thu Jan 21 08:32:10 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ChipShover Python API Documentation
======================================

ChipSHOVER is the Precision Position Producer, and consists of the full
chain of a physical XYZ table, mounts, electronic controller, and Python
interface. The control electronics (called ChipShover-One) are based on the
Marlin 3D printer firmware, meaning they use standard G-Codes for PC based
control of its position and various other functionality.

This Python API is designed as a simple way to control the ChipSHOVER-One
from Jupyter notebooks or other Python scripts/programs. You can use this
ChipShover Python API with other 3D printed based mainboards - we specifically
used standard 3D printer firmware & G-Codes to make it easier to maintain
the same Pythin API interface.

.. toctree::
   :maxdepth: 2

.. automodule:: chipshover.cs

.. autoclass:: ChipShover
    :members:

This documentation is part of the ChipShover Python API.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this ChipShover Python API software and associated documentation files
(the "Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom
the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

ChipShover is a registered trademark of NewAE Technology Inc.
    
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
