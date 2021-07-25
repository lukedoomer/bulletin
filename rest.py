import sys, configparser
from lcd import LCD

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

from multiprocessing import Process

class ShowText(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('content')
    
    proc = None

    def __init__(self, **kwargs):
        self.lcd = kwargs['lcd']

    def post(self):
        self.delete()
        args = ShowText.parser.parse_args()
        Process(target=self.lcd.tts, args=(args['content'],)).start()   # comment out if you don't have homeassistant installed
        ShowText.proc = Process(target=self.lcd.showtext, args=(args['content'],), daemon=True)
        ShowText.proc.start()
        return args['content'], 201

    def delete(self):
        if ShowText.proc != None:
            ShowText.proc.terminate()
        self.lcd.blank()
        return '', 204


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    app = Flask(__name__)
    api = Api(app)

    ##
    ## Actually setup the Api resource routing here
    ##
    api.add_resource(ShowText, '/text', resource_class_kwargs={ 'lcd': LCD(config) })
    
    app.run(host='0.0.0.0', debug=True)
