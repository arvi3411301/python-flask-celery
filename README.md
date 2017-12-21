# python-flask-celery

This project consists of a basic Hasura project with a simple celery worker based on Python-Flask app running on it. Once this app is deployed on a Hasura cluster, you will have the app running at `https://www.<cluster-name>.hasura-app.io`

## Sections

* [Introduction](#introduction)
* [Quickstart](#quickstart)
* [Adding your own code](#adding-your-existing-code)
* [FAQ](#faq)

## Introduction

This quickstart project comes with the following by default:

1. A basic Hasura project

## Quickstart

Follow this section to get this project working. Before you begin, ensure you have the latest version of [hasura cli tool](https://docs.hasura.io/0.15/manual/install-hasura-cli.html) installed.

### Step 1: Getting the project

```sh
$ hasura quickstart python-flask-celery
$ cd python-flask-celery
```

The above command does the following:
1. Creates a new folder in the current working directory called `python-flask-celery`
2. Creates a new free Hasura cluster for you and sets that cluster as the default cluster for this project
3. Initializes `python-flask-celery` as a git repository and adds the necessary git remotes.

### Step 2: Deploying this project

To deploy the project:

```sh
$ git add .
$ git commit -m "Initial Commit"
$ git push hasura master
```
When you push for the first time, it might take sometime. Next time onwards, it is really fast.

Once the above commands are executed successfully, head over to `https://app.<cluster-name>.hasura-app.io` (in this case `https://app.h34-excise98-stg.hasura-app.io`) to view your app.

## Adding your existing code
The microservice[1] sample code is inside the `microservices/app/app` directory. You can copy all your existing code directly inside this directory, and start deploying your own code to Hasura cluster.

### Step 1: Add your code in the microservices directory
Copy all your exising source code in `microservices/app/app` directory or replace the `microservices/app/app` directory with your app directory. Ensure that the structure of the directory is coherent with the current structure.

### Step 2: Using Celery Module

Minimal Example of using Celery with Flask:

```python
from flask import Flask
from celery import Celery

flask_app = Flask(__name__)

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

flask_app.config.update(
    CELERY_BROKER_URL='redis://session-redis.hasura:6379/1',
    CELERY_RESULT_BACKEND='redis://session-redis.hasura:6379/1'
)
celery = make_celery(flask_app)


@celery.task()
def add_together(a, b):
    return a + b
```

This task can now be called in the background:

```python
task = add_together.apply_async((a,b))
print (task.id)
```

Result of this task can be fetched using the code below:

```python
task = add_together.AsyncResult(task_id)
```

You can now run the worker by executing our program with the worker argument:

```bash
ENTRYPOINT celery -A src.celery worker -B --loglevel=info
```

### Step 3: Git add and commit
```
$ git add .
$ git commit -m "Added my Celery code"
```

### Step 4: Deploy
```
$ git push hasura master
```
Now your application should be running at: `https://app.<cluster-name>.hasura-app.io`

[1] a microservice is a running application on the Hasura cluster. This could be an app, a web app, a Javascript app etc.

## Hasura API console

Every Hasura cluster comes with an api console that gives you a GUI to test out the BaaS features of Hasura. To open the api console

```sh
$ hasura api-console
```

## Custom Microservice

There might be cases where you might want to perform some custom business logic on your apis. For example, sending an email/sms to a user on sign up or sending a push notification to the mobile device when some event happens. For this, you would want to create your own custom microservice which does these for you on the endpoints that you define.

This quickstart comes with one such custom microservice written in Python using the Celery module. Check it out in action at `https://app.cluster-name.hasura-app.io` . Currently, it just returns a JSON response of adding a task which adds two random numbers at that endpoint.

In case you want to use another language/framework for your custom microservice. Take a look at our docs to see how you can add a new custom microservice.

## Files and Directories

The project (a.k.a. project directory) has a particular directory structure and it has to be maintained strictly, else `hasura` cli would not work as expected. A representative project is shown below:

```
.
├── hasura.yaml
├── clusters.yaml
├── conf
│   ├── authorized-keys.yaml
│   ├── auth.yaml
│   ├── ci.yaml
│   ├── domains.yaml
│   ├── filestore.yaml
│   ├── gateway.yaml
│   ├── http-directives.conf
│   ├── notify.yaml
│   ├── postgres.yaml
│   ├── routes.yaml
│   └── session-store.yaml
├── migrations
│   ├── 1504788327_create_table_user.down.yaml
│   ├── 1504788327_create_table_user.down.sql
│   ├── 1504788327_create_table_user.up.yaml
│   └── 1504788327_create_table_user.up.sql
└── microservices
    └── www
        ├── app/
        ├── k8s.yaml
        └── Dockerfile
```

### `hasura.yaml`

This file contains some metadata about the project, namely a name, description and some keywords. Also contains `platformVersion` which says which Hasura platform version is compatible with this project.

### `clusters.yaml`

Info about the clusters added to this project can be found in this file. Each cluster is defined by it's name allotted by Hasura. While adding the cluster to the project you are prompted to give an alias, which is just hasura by default. The `kubeContext` mentions the name of kubernetes context used to access the cluster, which is also managed by hasura. The `config` key denotes the location of cluster's metadata on the cluster itself. This information is parsed and cluster's metadata is appended while conf is rendered. `data` key is for holding custom variables that you can define.

```yaml
- name: h34-ambitious93-stg
  alias: hasura
  kubeContext: h34-ambitious93-stg
  config:
    configmap: controller-conf
    namespace: hasura
  data: null
```
