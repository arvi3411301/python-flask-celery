from flask import Flask
from celery import Celery


app = Flask(__name__)

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

# Configure Celery with flask
app.config.update(
    CELERY_BROKER_URL='redis://redis.hasura:6379/1',
    CELERY_RESULT_BACKEND='redis://redis.hasura:6379/1'
)
celery = make_celery(app)

from .server import *
