import time, ST7789, textwrap, requests, json
import RPi.GPIO as GPIO

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from pydub import AudioSegment
from pydub.playback import play

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
        self.blank()

    def tts(self, content):
        headers = {'Authorization': 'Bearer {}'.format(self.config['homeassistant']['token'])}
        data = {'message': content, 'platform': 'google_translate', 'language': 'zh-tw'}
        r = requests.post(self.config['homeassistant']['url'], headers=headers, json=data)

        file = NamedTemporaryFile()
        with open(file.name, "wb") as fp:
            r = requests.get(r.json()['url'])
            fp.write(r.content)
        sound = AudioSegment.from_file(file.name, format="mp3")
        play(sound)
        
    def showtext(self, content):
        font = ImageFont.truetype(self.config['text']['font'], self.config.getint('text', 'size'))
        content = textwrap.fill(text = content, width = int(self.disp.width / self.config.getint('text', 'size') / 0.8))
        offset = int(self.config.getint('text', 'size') / 4)    # offset of moving text animation
        
        while True:
            if time.localtime().tm_sec % 20 == 0:   # avoid screen burn-in
                self.blank()
                
            else:
                offset = - offset

                self.draw.rectangle((0, 0, self.disp.width, self.disp.height), (0, 0, 0))
                self.draw.text(
                    xy = (self.disp.width / 2 + offset, self.disp.height / 2),
                    text = content,
                    font = font,
                    fill = self.config['text']['color'],
                    anchor = 'mm')
                self.disp.display(self.img)
            time.sleep(1)

    def blank(self):
        self.img = Image.new('RGB', (self.disp.width, self.disp.height), color=(0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.disp.display(self.img)
