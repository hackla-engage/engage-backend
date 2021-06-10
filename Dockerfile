FROM python:3.8-slim
# A side effect of using alpine is you must build psycopg2 from source
RUN apt-get update && apt-get install -y python3-dev build-essential curl postgresql-contrib netcat
ENV LIBRARY_PATH=/lib:/usr/lib
RUN pip install pipenv
COPY . /engage_backend_service
WORKDIR /engage_backend_service
RUN pipenv install --system --deploy