# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_ili9341`
====================================================

Display driver for ILI9341

* Author(s): Scott Shawcroft

Implementation Notes
--------------------

**Hardware:**

* Adafruit PiTFT 2.2" HAT Mini Kit - 320x240 2.2" TFT - No Touch
  <https://www.adafruit.com/product/2315>
* Adafruit PiTFT 2.4" HAT Mini Kit - 320x240 TFT Touchscreen
  <https://www.adafruit.com/product/2455>
* Adafruit PiTFT - 320x240 2.8" TFT+Touchscreen for Raspberry Pi
  <https://www.adafruit.com/product/1601>
* PiTFT 2.8" TFT 320x240 + Capacitive Touchscreen for Raspberry Pi
  <https://www.adafruit.com/product/1983>
* Adafruit PiTFT Plus 320x240 2.8" TFT + Capacitive Touchscreen
  <https://www.adafruit.com/product/2423>
* PiTFT Plus Assembled 320x240 2.8" TFT + Resistive Touchscreen
  <https://www.adafruit.com/product/2298>
* PiTFT Plus 320x240 3.2" TFT + Resistive Touchscreen
  <https://www.adafruit.com/product/2616>
* 2.2" 18-bit color TFT LCD display with microSD card breakout
  <https://www.adafruit.com/product/1480>
* 2.4" TFT LCD with Touchscreen Breakout Board w/MicroSD Socket
  <https://www.adafruit.com/product/2478>
* 2.8" TFT LCD with Touchscreen Breakout Board w/MicroSD Socket
  <https://www.adafruit.com/product/1770>
* 3.2" TFT LCD with Touchscreen Breakout Board w/MicroSD Socket
  <https://www.adafruit.com/product/1743>
* TFT FeatherWing - 2.4" 320x240 Touchscreen For All Feathers
  <https://www.adafruit.com/product/3315>

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    # used for typing only
    from typing import Any

    from fourwire import FourWire
except ImportError:
    pass

from busdisplay import BusDisplay

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ILI9341.git"

_INIT_SEQUENCE = (
    b"\x01\x80\x80"  # Software reset then delay 0x80 (128ms)
    b"\xef\x03\x03\x80\x02"
    b"\xcf\x03\x00\xc1\x30"
    b"\xed\x04\x64\x03\x12\x81"
    b"\xe8\x03\x85\x00\x78"
    b"\xcb\x05\x39\x2c\x00\x34\x02"
    b"\xf7\x01\x20"
    b"\xea\x02\x00\x00"
    b"\xc0\x01\x23"  # Power control VRH[5:0]
    b"\xc1\x01\x10"  # Power control SAP[2:0];BT[3:0]
    b"\xc5\x02\x3e\x28"  # VCM control
    b"\xc7\x01\x86"  # VCM control2
    b"\x37\x01\x00"  # Vertical scroll zero
    b"\x3a\x01\x55"  # COLMOD: Pixel Format Set
    b"\xb1\x02\x00\x18"  # Frame Rate Control (In Normal Mode/Full Colors)
    b"\xb6\x03\x08\x82\x27"  # Display Function Control
    b"\xf2\x01\x00"  # 3Gamma Function Disable
    b"\x26\x01\x01"  # Gamma curve selected
    b"\xe0\x0f\x0f\x31\x2b\x0c\x0e\x08\x4e\xf1\x37\x07\x10\x03\x0e\x09\x00"  # Set Gamma
    b"\xe1\x0f\x00\x0e\x14\x03\x11\x07\x31\xc1\x48\x08\x0f\x0c\x31\x36\x0f"  # Set Gamma
    b"\x11\x80\x78"  # Exit Sleep then delay 0x78 (120ms)
    b"\x29\x80\x78"  # Display on then delay 0x78 (120ms)
)


# pylint: disable=too-few-public-methods
class ILI9341(BusDisplay):
    """
    ILI9341 display driver

    :param FourWire bus: bus that the display is connected to
    """

    def __init__(self, bus: FourWire, *, bgr: bool = False, invert: bool = False, **kwargs: Any):
        init_sequence = _INIT_SEQUENCE
        if bgr:
            init_sequence += b"\x36\x01\x30"  # _MADCTL Default rotation plus BGR encoding
        else:
            init_sequence += b"\x36\x01\x38"  # _MADCTL Default rotation plus RGB encoding
        if invert:
            init_sequence += b"\x21\x00"  # _INVON

        super().__init__(bus, init_sequence, **kwargs)
