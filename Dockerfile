FROM python:3.8-slim
RUN apt-get update && apt-get install -y curl postgresql-contrib netcat
ENV LIBRARY_PATH=/lib:/usr/lib
COPY . /engage_backend_service
WORKDIR /engage_backend_service
RUN pip install -r requirements.txt
CMD ["scripts/rundev.sh"]