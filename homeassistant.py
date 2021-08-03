import requests

from pydub import AudioSegment
from pydub.playback import play

from tempfile import NamedTemporaryFile

class homeassistant:
        
    @staticmethod
    def tts(url, token, content):
        headers = {'Authorization': 'Bearer {}'.format(token)}
        data = {'message': content, 'platform': 'google_translate', 'language': 'zh-tw'}
        r = requests.post(url, headers=headers, json=data)

        file = NamedTemporaryFile()
        with open(file.name, "wb") as fp:
            r = requests.get(r.json()['url'])
            fp.write(r.content)
        sound = AudioSegment.from_file(file.name, format="mp3")
        play(sound)