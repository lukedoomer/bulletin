import time, ST7789, textwrap, json, itertools
import RPi.GPIO as GPIO

from PIL import Image, ImageDraw, ImageFont, ImageSequence

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
        self.show_blank()

        self.font = ImageFont.truetype(self.config['notify']['font'], self.config.getint('notify', 'size'))
        self.offset = int(self.config.getint('notify', 'size') / 6)   # offset of moving text animation
        
        self.gif_index = 0
        self.gif = list()
        gif = Image.open(self.config['background']['gif'])
        for frame in ImageSequence.Iterator(gif):
            self.gif.append(frame.resize((self.disp.width, self.disp.height)))

        self.images_index = 0
        self.images = list()

    def set_images(self, images):
        for i in range(len(images)):
            images[i] = images[i].resize((self.disp.width, self.disp.height))
        self.images = images

    def show_image(self, image):
        self.disp.display(image)

    def show_batch_images(self):
        if self.images:
            if self.images_index >= len(self.images):
                self.images_index = 0
            self.show_image(self.images[self.images_index])
            self.images_index += 1

    def show_text_on_gif(self, text):
        if self.gif_index >= len(self.gif):
            self.gif_index = 0
        image = self.gif[self.gif_index].copy()
        self.draw_text(text, bg=image)
        self.show_image(image)
        self.gif_index += 1

    def show_text_on_blank(self, text):
        image = self.draw_blank()
        self.draw_text(text, bg=image)
        self.disp.display(image)

    def draw_text(self, text, bg):
        text = textwrap.fill(text = text, width = int(self.disp.width / self.config.getint('notify', 'size') / 0.8))
        self.offset = - self.offset

        draw = ImageDraw.Draw(bg)
        draw.text(
            xy = (self.disp.width / 2 + self.offset, self.disp.height / 2),
            text = text,
            font = self.font,
            fill = self.config['notify']['color'],
            anchor = 'mm')

    def draw_blank(self):
        image = Image.new('RGB', (self.disp.width, self.disp.height), color=(0, 0, 0))
        return image

    def show_blank(self):
        self.disp.display(self.draw_blank())
