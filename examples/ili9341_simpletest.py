"""
This test will initialize the display using displayio
and draw a solid red background
"""

import board
import displayio
import adafruit_ili9341

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10

displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)

display = adafruit_ili9341.ILI9341(display_bus)

# Make the display context
splash = displayio.Group(max_size=10)
display.show(splash)

color_bitmap = displayio.Bitmap(320, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFF0000

try:
    bg_sprite = displayio.TileGrid(color_bitmap,
                                   pixel_shader=color_palette,
                                   position=(0, 0))
except TypeError:
    bg_sprite = displayio.TileGrid(color_bitmap,
                                   pixel_shader=color_palette,
                                   x=0, y=0)
splash.append(bg_sprite)

while True:
    pass
