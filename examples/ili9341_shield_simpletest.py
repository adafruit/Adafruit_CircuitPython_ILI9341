"""
This test will initialize the display using displayio and draw a solid green
background, a smaller purple rectangle, and some yellow text. All drawing is done
using native displayio modules.

Pinouts are for the 2.8" TFT Shield
"""
import board
import displayio
import terminalio
import adafruit_ili9341

spi = board.SPI()
tft_cs = board.D10
tft_dc = board.D9

displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

# Make the display context
splash = displayio.Group(max_size=10)
display.show(splash)

# Draw a green background
color_bitmap = displayio.Bitmap(320, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00 # Bright Green

bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)

splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(280, 200, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x65328F # Blinka Purple
inner_sprite = displayio.TileGrid(inner_bitmap,
                                  pixel_shader=inner_palette,
                                  x=20, y=20)
splash.append(inner_sprite)

# Draw some text the manual way!
font_palette = displayio.Palette(2)
font_palette.make_transparent(0)
font_palette[1] = 0xFFFF00 # Yellow

text_group = displayio.Group(max_size=20, scale=3, x=57, y=120)
text = "Hello World!"
x = 0

for character in text:
    glyph = terminalio.FONT.get_glyph(ord(character))
    position_x = x + glyph.dx
    position_y = 0 - round((glyph.height - glyph.dy) / 2) # Center text vertically
    face = displayio.TileGrid(glyph.bitmap, pixel_shader=font_palette,
                              default_tile=glyph.tile_index,
                              tile_width=glyph.width, tile_height=glyph.height,
                              x=position_x, y=position_y)
    text_group.append(face)
    x += glyph.shift_x

splash.append(text_group)

while True:
    pass
