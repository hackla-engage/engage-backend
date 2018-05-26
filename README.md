
# CouncilTag
Website: https://council-tag.herokuapp.com
API documentation: https://council-tag.herokuapp.com/docs

## Dev Setup

To setup development environment:

1. Clone this repo

2. Download virtualenv, if not already installed. After creating an virtualenv, download 
dependecies in the `requirements.txt`.

3. Download the Postgres libraries for your platform and PgAdmin, the GUI database manageer

4. Make sure the `DEBUG` value in the `settings.py` file is set to True if you are running locally
  1. To set DEBUG to true set environment variable ```CouncilTag=local```

5. Make sure that your Postgres has a `counciltag` database in it

6. Open PgAdmin 

7. If its your first time, setting up the dev environment, type the following commands:

`python manage.py migrate`

`python manage.py populate_tags`

`python manage.py scrape_data`

In order, these commands will 1) create the SQL tables needed, 2) load our list of tags, 3) load up a set of live data from the City of Santa Monica

8. Run `python manage.py runserver` to stat the python server. You can go to http://localhost:8000/docs 


## Continous Delivery

We have setup a continous integration with Heroku. When you push to the `prod` branch on this repo, this will trigger a build on the server. This will also run the Django test suite. If the tests fail, the build will not go through. 

## Django documentation
If you are new to using Django, you can read up more about it here:
https://docs.djangoproject.com/en/2.0/

