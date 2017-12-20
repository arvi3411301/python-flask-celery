from src import app, celery
from flask import jsonify, request, url_for
import requests
import json
from random import *

@celery.task()
def add_together(a, b):
    return a + b

@app.route("/")
def hello():
    a = randint(1, 100)
    b = randint(1, 100)
    task = add_together.apply_async((a,b))
    return jsonify({
        'a': a,
        'b': b,
        'task_url': url_for('taskstatus', task_id=task.id)
    })

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = add_together.AsyncResult(task_id)
    if task.status == 'SUCCESS':
        response = {
                    'state': task.state,
                    'result': task.result
                    }
    else:
        # something went wrong in the background job
        response = {
                    'state': task.state,
                }
    return jsonify(response)
