Changes until now:
==================

1. [Restructuring BLueprints.](discussion/blueprints)
2. [Restructuring models folder.](discussion/models)
3. [Putting together the error classes and registering them with the app instance.](discussion/errors.py)
4. Creating permission classes and permission decorator.[permissions](discussion/permission,py) [decorator](discussion/utils.py)
5. Adding paginagion files and classes with model, filters and schema fields. [pagination base class](discussion/utils.py)
6. Almost Full covering unittests

Ongoing changes:
==================

- Open-api and Swager
- SQl and Postgresql
- implementing Caching and Redis
- Editing loggers and log files
- Restructuring schemas
- Adding installation and requirements to the README file
- Changing root directory of the application
- Adding id, is\_active, created\_at and modified\_at fields to all models

Installation:
------------------

To get started, clone the project using:

`git clone git@github.com:danadarvishzadeh/flask-app.git`

From inside `flask-app`, create a virtual environment using:

`python -m venv venv`

Activate virtual environment using:

`. venv/bin/activate`

Then you can install the project requirements using:

`pip install -r requirements.txt`

After that, set `FLASK_APP` and `FLASK_ENV` environment variables using:
```
export FLASK_APP=discussion.app
export FLASK_ENV=development
```

But be aware that this setting will be reset each time you close your shell session.

And finally, you can run the app using:

`flask run`
