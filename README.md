Changes until now:
==================

1. [Restructuring BLueprints.](discussion/blueprints)
2. [Restructuring models folder.](discussion/models)
3. [Putting together the error classes and registering them with the app instance.](discussion/errors.py)
4. Creating permission classes and permission decorator.[permissions](discussion/permission,py) [decorator](discussion/utils.py)
5. Adding paginagion files and classes with model, filters and schema fields. [pagination base class](discussion/utils.py)
6. Almost Full covering unittests
7. Adding installation and requirements to the README file
8. Adding id, is\_active, created\_at and modified\_at fields to all models
9. Restructuring schemas
10. Changing model fields for permissions to work indipendent of models
11. Changing paginators to accept filters
12. UTC dates
13. Changing root directory of the application

Ongoing changes:
==================

- Open-api and Swager
- implementing Caching and Redis
- Editing loggers and log files
- SQl and Postgresql
- view refactoring
- models base class
- overal refactor
- OpenID Connect
- Oaouth2
- sever side authorization (redis)


Questions:
==================
1. Best practices of handling exceptions.


Installation:
==================
------------------

To get started, clone the project using:

```
git clone git@github.com:danadarvishzadeh/flask-app.git
```

From inside `flask-app`, create a virtual environment using:

```
python -m venv venv
```

Activate virtual environment using:

```
. venv/bin/activate
```

Then you can install the project requirements using:

```pip install -r requirements.txt
```

After that, set `FLASK_APP` and `FLASK_ENV` environment variables using:
```
export FLASK_APP=discussion.app
export FLASK_ENV=development
```

But be aware that this setting will be reset each time you close your shell session.

And finally, you can run the app using:

```
flask run
```
