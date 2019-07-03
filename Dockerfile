FROM python:3.6-alpine
# A side effect of using alpine is you must build psycopg2 from source
RUN apk update && apk add curl postgresql-dev postgresql-contrib build-base python3-dev musl-dev netcat-openbsd jpeg-dev zlib-dev autoconf automake g++ make
ENV LIBRARY_PATH=/lib:/usr/lib
RUN pip install pipenv
COPY . /engage_backend_service
WORKDIR /engage_backend_service
RUN pipenv install --system --deploy