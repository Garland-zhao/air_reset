from flask import Flask
from celery import Celery


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://192.168.2.9:6379/6'
app.config['CELERY_RESULT_BACKEND'] = 'redis://192.168.2.9:6379/7'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
