FROM python:3.8-slim
RUN apt-get update && apt-get install -y libpq-dev python3-dev
ENV LIBRARY_PATH=/lib:/usr/lib
COPY requirements.txt /engage_backend_service/requirements.txt
WORKDIR /engage_backend_service
RUN pip install -r requirements.txt
COPY . /engage_backend_service
RUN ["python", "manage.py", "collectstatic", "--no-input"]
CMD ["scripts/rundev.sh"]