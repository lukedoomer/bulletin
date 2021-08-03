import time, ST7789, textwrap, json
import RPi.GPIO as GPIO

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from tempfile import NamedTemporaryFile

class LCD:
    def __init__(self, config):
        self.config = config

        # Create TFT LCD display class.
        self.disp = ST7789.ST7789(
            rotation = 270,
            port = 0,                     # SPI port
            cs = ST7789.BG_SPI_CS_FRONT,  # SPI port Chip-select channel: BG_SPI_CS_BACK or BG_SPI_CS_FRONT
            dc = 9,                       # BCM pin used for data/command
            backlight = 1,
            spi_speed_hz = 80 * 1000 * 1000,
            offset_left = 0
        )
        # Initialize display.
        self.drawblank()

        self.font = ImageFont.truetype(self.config['text']['font'], self.config.getint('text', 'size'))
        self.offset = self.config.getint('text', 'offset')

        self.gif = Image.open(self.config['background']['gif'])
        self.frame = 0

    def drawgif(self):
        self.frame += 1
        try:
            self.gif.seek(self.frame)
        except EOFError:
            self.frame = 0
        self.img = self.gif.resize((self.disp.width, self.disp.height))
        self.draw = ImageDraw.Draw(self.img)

    def showtext(self, content, bg):
        if bg:
            self.drawgif()
        else:
            self.drawblank()

        content = textwrap.fill(text = content, width = int(self.disp.width / self.config.getint('text', 'size') / 0.8))
        self.offset = - self.offset

        self.draw.text(
            xy = (self.disp.width / 2 + self.offset, self.disp.height / 2),
            text = content,
            font = self.font,
            fill = self.config['text']['color'],
            anchor = 'mm')
        self.disp.display(self.img)

    def drawblank(self):
        self.img = Image.new('RGB', (self.disp.width, self.disp.height), color=(0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)

    def showblank(self):
        self.drawblank()
        self.disp.display(self.img)