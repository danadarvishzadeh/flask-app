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
14. Open-api and Swager
15. View refactoring
16. Overal refactor
17. Models base class
18. Unify responses
19. External dependencies error
20. Editing loggers and log files
21. OAuth2
22. OpenID Connect
23. Authorization using redis
24. Caching
25. Pagination


Ongoing changes:
==================

- Multiple sessions
- paranoid token
- Email and reset password
- MongoDB
- SQl and Postgresql

Redis Schema:
==================

### access token  -> key: value
### refresh token -> key: value
### user_id       -> list [ip]
### ip            -> map[access_token, refresh_token, User-Agent, last-login]


Installation:
==================

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

```
pip install -r requirements.txt
```

After that, set `FLASK_APP` and `FLASK_ENV` environment variables using:
```
export FLASK_APP=discussion.app
export FLASK_ENV=development
```

You need to start `redis-server` and `postgresql` using:
```
sudo systemctl start postgresql.service
sudo systemctl start redis-server.service
```

You also need to create a postgresql database for the application and run migrations.

Database name is specified and can be changed in the config file.\
Creation of the database:

```
example@example:~$ psql postgres
postgres=# CREATE DATABASE [database name]
```

Run migrations using:
```
flask db upgrade
```


And then, you can run the app using:

```
flask run
```

To see swagger documentation of the API, go to [/doc/swagger](http://localhost:5000/doc/swagger
) . You can visit the following address on your computer:
```
http://localhost:5000/doc/swagger
```
