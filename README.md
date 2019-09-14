
# Engage Backend

- Live Website: https://sm.engage.town
- Live API Endpoint: http://backend.engage.town/api/
- Live API Documentation: https://backend.engage.town/swagger/
- Local API Endpoint http://localhost:8000/api
- Local API Documentation http://localhost:8000/swagger/

## Dev Setup
To setup the development environment:

0. Install redis [https://redis.io/download](https://redis.io/download)

 * Make sure you use version 4.0.0

 * Compiling is very slow due to the testing suite.

   * if you use MacOS, use ```brew install redis```

   * if ubuntu, use guide from [digital ocean](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04)

1. Clone this repo

2. Set up a virtualenv and install all Python packages.

`pip install virtualenv`

`virtualenv env -p /path/to/python3.6`
  * if you don't know your path to python, run `which python3` and use the path returned

`source env/bin/activate`

`pipenv install`

3. Setup Postgres and PgAdmin for your platform if needed. PgAdmin is a useful GUI database manager.

 * Make sure you are using postgres from major vrsion 10, not 11

4. Create the `counciltag` database if it does not exist.

5. Create a database user, give the user a password and grant the user permissions for `counciltag`.

6. Add the following environment variables for the project. You'll need database info, django secret key and 'CouncilTag' to run the project in DEBUG mode.

 ```
 POSTGRES_DB=counciltag
 POSTGRES_USER=REPLACEME
 POSTGRES_PASSWORD=REPLACEME
 DJANGO_SECRET_KEY=someuniqueunpredictablevalue
 SENDGRIDKEY="SG.-some_long_string"
 RECAPTCHAKEY="some_string"
 CouncilTag=debug
 REDIS_HOSTNAME=localhost
 POSTGRES_HOSTNAME=localhost
 ```

7. To run tests on the package set these environment variables:
```
POSTGRES_USER=<Some user with DB create rights or who owns $POSTGRES_DB>
POSTGRES_PASSWORD=<Password for $POSTGRES_USER>
POSTGRES_DB=<Some DB that already exists or that you have create rights for>
DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost/$POSTGRES_DB?sslmode=true
CouncilTag=test
DJANGO_SECRET_KEY=examplesecretkeydonotuseinprod
SENDGRIDKEY=SG.-thisisnotarealkeylol
REDIS_HOSTNAME=localhost
POSTGRES_HOSTNAME=localhost
```

8. Then, run `python manage.py test -k`
* -k keeps the existing database and is not necessary if your user is granted create rights on the system

9. If it's your first time setting up the dev environment, run the following commands. In this order, these commands will 1) create the SQL tables needed, 2) load our list of tags, 3) scrape live data from the City of Santa Monica.

`python manage.py migrate`

`python manage.py populate_tags`

`python manage.py scrape_data`

10. Then edit `CouncilTags/urls.py` to switch to localhost.

```
# url="https://backend.engage.town/api",
url="http://localhost:8000/api",
```

11. (optional) If you want to scrape agendas nightly for a committee you must start the celery beat worker. My recommendation is to output the errors and logs to a text file like beats.tst

`celery -A CouncilTag beat -l debug > beat.tst 2>&1 &`

12. (optional) If you want to process the PDFs for upcoming committee meetings you must start the celery worker. My recommendation is to output the errors and logs to a text file like worker.tst

`celery -A CouncilTag worker -l debug > worker.tst 2>&1 &`

13. Finally, start the server.

`python manage.py runserver`

You can go to `http://localhost:8000/swagger/` to look at the docs and interact with the API.

14. Alternatively use Docker

* We have included a docker-compose.yml so that you can edit this repository and run the backend without having to configure all the requirements. To build the combined images required for the repository run:
`docker-compose build`

* If you are testing the frontend against the docker backend then you should uncomment line 8 from `runservices.sh` to download agendas for 2018 (You can add, change, or remove years on that line. Years should be separated by a comma. Be patient, web scraping from the Santa Monica site is incredibly slow.)

* Once built, you can run the repository's configuration with
`docker-compose up`

* Navigate to https://localhost:8000/swagger/ to test


## Continous Delivery

We have setup continous integration and deployment on CircleCI.

When you push to the `master` branch on this repo, this will trigger a build on the server and also run the Django test suite. If the tests fail, the build will not go through.


##
