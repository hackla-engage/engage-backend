FROM python:3.6.5
ENV PYTHONUNBUFFERED 1

COPY . /engage_backend_service/
WORKDIR /engage_backend_service/

RUN apt-get update && apt-get -y install postgresql
RUN pip install pipenv
RUN pipenv install --system

# Expose is NOT supported by Heroku
# EXPOSE 8000

# Run the image as a non-root user

CMD pip --version
