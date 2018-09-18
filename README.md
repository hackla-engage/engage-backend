
# CouncilTag

- Live Website: https://sm.engage.town
- Live API Endpoint: http://backend.engage.town/api/
- Live API Documentation: https://backend.engage.town/swagger/
- Local API Endpoint http://localhost:8000/api
- Local API Documentation http://localhost:8000/swagger/

## Dev Setup
To setup the development environment:

1. Clone this repo

2. Setup a virtualenv and install all Python packages.

`pip install -r requirements.txt`

3. Setup Postgres and PgAdmin for your platform if needed. PgAdmin is a useful GUI database manager.

4. Create the `counciltag` database if it does not exist.

5. Create a database user, give the user a password and grant the user permissions for `counciltag`.

6. Add the following environmental variables for the project. You'll need database info, django secret key and 'CouncilTag' to run the project in DEBUG mode. 

 ```
 DB_NAME=counciltag
 DB_USER=REPLACEME
 DB_PASSWORD=REPLACEME
 DJANGO_SECRET_KEY=someuniqueunpredictablevalue
 SENDGRIDKEY="SG.-some_long_string"
 RECAPTCHAKEY="some_string"
 CouncilTag=debug
 ```

7. To run tests on the package set these environment variables:
```
POSTGRES_USER=<Some user with DB create rights or who owns $POSTGRES_DB>
POSTGRES_PASSWORD=<Password for $DB_TEST_USER>
POSTGRES_DB=<Some DB that already exists or that you have create rights for>
DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost/$POSTGRES_DB?sslmode=true
CouncilTag=test
DJANGO_SECRET_KEY=examplesecretkeydonotuseinprod
SENDGRIDKEY=SG.-thisisnotarealkeylol
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


## Continous Delivery

We have setup continous integration and deployment on CircleCI.

When you push to the `master` branch on this repo, this will trigger a build on the server and also run the Django test suite. If the tests fail, the build will not go through.


## Django Documentation

If you are new to using Django, you can read up more about it here:
https://docs.djangoproject.com/en/2.0/

