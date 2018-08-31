
# CouncilTag

- Live Website: https://engage-santa-monica.herokuapp.com
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
 CouncilTag=local
 ```

7. If it's your first time setting up the dev environment, run the following commands. In this order, these commands will 1) create the SQL tables needed, 2) load our list of tags, 3) scrape live data from the City of Santa Monica.

`python manage.py migrate` 

`python manage.py populate_tags` 

`python manage.py scrape_data` 

8. Then edit `CouncilTags/urls.py` to switch to localhost.

```
# url="https://backend.engage.town/api",
url="http://localhost:8000/api",
```

9. Finally, start the server.

`python manage.py runserver`

You can go to `http://localhost:8000/swagger/` to look at the docs and interact with the API. 


## Continous Delivery

We have setup continous integration and deployment with Heroku and CircleCI.

When you push to the `prod` branch on this repo, this will trigger a build on the server and also run the Django test suite. If the tests fail, the build will not go through.


## Django Documentation

If you are new to using Django, you can read up more about it here:
https://docs.djangoproject.com/en/2.0/

