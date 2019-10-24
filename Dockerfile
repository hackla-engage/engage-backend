FROM python:3.7-alpine
# A side effect of using alpine is you must build psycopg2 from source
RUN pip install --upgrade pip
RUN apk update && apk add alpine-sdk postgresql-dev netcat-openbsd jpeg-dev libffi-dev zlib-dev 
ENV LIBRARY_PATH=/lib:/usr/lib
COPY . /engage_backend_service
WORKDIR /engage_backend_service
RUN pip install -r requirements.txt