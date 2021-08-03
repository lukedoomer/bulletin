import sys, configparser, datetime
from lcd import LCD
from homeassistant import homeassistant

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource, inputs

from apscheduler.schedulers.background import BackgroundScheduler

class ShowText(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('content')
    parser.add_argument('bg', type=inputs.boolean, default=True)

    scheduler = BackgroundScheduler()
    scheduler.start()

    def __init__(self, **kwargs):
        self.lcd = kwargs['lcd']

    def post(self):
        self.delete()
        args = ShowText.parser.parse_args()
        ShowText.scheduler.add_job(homeassistant.tts,
            'date', run_date=datetime.datetime.now(),
            args=[self.lcd.config['homeassistant']['url'], self.lcd.config['homeassistant']['token'], args['content']])   # comment out if you don't have homeassistant installed
        ShowText.scheduler.add_job(self.lcd.showtext,
            'interval', seconds=self.lcd.config.getfloat('background', 'interval'),
            args=[args['content'], args['bg']], id='showtext')
        ShowText.scheduler.add_job(self.lcd.showblank, 'interval', minutes=1, id='showblank')   # avoid screen burn-in
        return args['content'], 201

    def delete(self):
        for job in ShowText.scheduler.get_jobs():
            job.remove()
        self.lcd.showblank()
        return '', 204


if __name__ == '__main__':
    config = configparser.ConfigParser(inline_comment_prefixes=';')
    config.read(sys.argv[1])

    app = Flask(__name__)
    api = Api(app)

    ##
    ## Actually setup the Api resource routing here
    ##
    api.add_resource(ShowText, '/text', resource_class_kwargs={ 'lcd': LCD(config) })

    app.run(host='0.0.0.0', debug=True)
