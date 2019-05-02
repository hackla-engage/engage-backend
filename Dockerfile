FROM python:3.6.5-alpine3.7

WORKDIR "/srv/engage-backend"

ENV PYTHONUNBUFFERED=1

# | build-base     | GCC tools |
# | postgresql-dev | psycopg2  |
# | libffi-dev     | bcrypt    |
# | libxslt-dev    | lxml      |
# | jpeg-dev       | Pillow    |
RUN apk add --no-cache build-base postgresql-dev libffi-dev libxslt-dev \
                       jpeg-dev \
    && pip install --upgrade pip \
    && pip install pipenv

EXPOSE 8000
VOLUME ["/srv/engage-backend"]

CMD ["sh", "/srv/engage-backend/runservices.sh"]
