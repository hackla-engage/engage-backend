FROM python:3.6.8
ENV PYTHONUNBUFFERED 1
RUN wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | apt-key add -
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
RUN apt-get update && apt-get install -y build-essential curl postgresql postgresql-contrib netcat
RUN pip install pipenv
COPY . /engage_backend_service
WORKDIR /engage_backend_service
RUN pipenv install --system --deploy