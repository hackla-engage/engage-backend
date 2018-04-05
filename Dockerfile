FROM python:3
ENV PYTHONUNBUFFERED 1

COPY . /code/
WORKDIR /code/

RUN apt-get update && apt-get -y install postgresql
RUN pip install pipenv
RUN pipenv install --system

EXPOSE 8000