import sys, configparser, datetime
from datetime import datetime, timedelta
from lcd import LCD
from homeassistant import homeassistant
from crypto import crypto

from flask import Flask, request
from flask_apscheduler import APScheduler
from apscheduler.events import EVENT_JOB_EXECUTED

from tempfile import NamedTemporaryFile
from PIL import Image, ImageSequence

app = Flask(__name__)

config = configparser.ConfigParser(inline_comment_prefixes=';')
config.read('settings')

lcd = LCD(config)

scheduler = APScheduler()

def listener(event):
    if 'candles' in event.job_id:
        lcd.set_images(list(event.retval.values()))

@app.route("/clear", methods=['GET'])
def remove_job():
    for job in scheduler.get_jobs():
        job.remove()
    lcd.show_blank()
    return '', 204

@app.route("/crypto", methods=['GET'])
def show_candles():
    remove_job()
    
    pairs = request.args.get('pair').split(',')

    scheduler.add_job(func=crypto.update_candles,
        trigger='date',
        run_date=datetime.now(),
        id='init_candles',
        args=[config['binance']['api_key'], config['binance']['api_secret'], pairs])

    scheduler.add_job(func=lcd.show_batch_images,
        trigger='interval', seconds=config.getint('binance', 'slide_interval'),
        id='show_candles')

    scheduler.add_job(func=crypto.update_candles,
        trigger='interval', seconds=config.getint('binance', 'update_interval'),
        id='update_candles',
        args=[config['binance']['api_key'], config['binance']['api_secret'], pairs])
        
    return request.args.get('pair'), 200

@app.route("/upload", methods=['POST'])
def upload_gif():
    interval = 1.0
    if 'interval' in request.form:
        interval = float(request.form.get('interval'))

    file = request.files['file']
    if file:
        tmpfile = NamedTemporaryFile()
        file.save(tmpfile.name)

        images = list()
        for frame in ImageSequence.Iterator(Image.open(tmpfile.name)):
            images.append(frame.copy())
        lcd.set_images(images)

        remove_job()

        scheduler.add_job(func=lcd.show_batch_images,
            trigger='interval', seconds=interval,
            id='show_images')

        return tmpfile.name, 201
    else:
        return '', 400

@app.route("/notify", methods=['POST'])
def show_text():
    text = request.form.get('text')
    now = datetime.now()
    end = now + timedelta(seconds=config.getint('notify', 'duration'))

    job = scheduler.get_job('show_candles')
    if job:
        job.reschedule(trigger='interval',
            seconds=job.trigger.interval.total_seconds(),
            start_date=end)
    job = scheduler.get_job('show_images')
    if job:
        job.reschedule(trigger='interval',
            seconds=job.trigger.interval.total_seconds(),
            start_date=end)
    
    scheduler.add_job(func=homeassistant.tts,
        trigger='date',
        run_date=now,
        id='tts',
        args=[config['homeassistant']['url'], config['homeassistant']['token'], text])   # comment out if you don't have homeassistant installed
    scheduler.add_job(func=lcd.show_text_on_gif,
        trigger='interval',
        seconds=lcd.config.getfloat('background', 'interval'),
        end_date=end,
        id='show_text',
        args=[text])

    return text, 201

if __name__ == '__main__':
    scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.add_listener(listener, EVENT_JOB_EXECUTED)
    scheduler.start()
    app.run(host='0.0.0.0', debug=True)
