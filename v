anyjson==0.3.3
appdirs==1.4.3
attrs==18.1.0
autopep8==1.3.2
  - pycodestyle [required: >=2.3, installed: 2.3.1]
backports.functools-lru-cache==1.4
bcrypt==3.1.4
  - cffi [required: >=1.1, installed: 1.11.5]
    - pycparser [required: Any, installed: 2.18]
  - six [required: >=1.4.1, installed: 1.10.0]
boto3==1.9.2
  - botocore [required: <1.13.0,>=1.12.2, installed: 1.12.2]
    - docutils [required: >=0.10, installed: 0.14]
    - jmespath [required: >=0.7.1,<1.0.0, installed: 0.9.3]
    - python-dateutil [required: <3.0.0,>=2.1, installed: 2.7.3]
      - six [required: >=1.5, installed: 1.10.0]
    - urllib3 [required: <1.24,>=1.20, installed: 1.22]
  - jmespath [required: >=0.7.1,<1.0.0, installed: 0.9.3]
  - s3transfer [required: <0.2.0,>=0.1.10, installed: 0.1.13]
    - botocore [required: >=1.3.0,<2.0.0, installed: 1.12.2]
      - docutils [required: >=0.10, installed: 0.14]
      - jmespath [required: >=0.7.1,<1.0.0, installed: 0.9.3]
      - python-dateutil [required: <3.0.0,>=2.1, installed: 2.7.3]
        - six [required: >=1.5, installed: 1.10.0]
      - urllib3 [required: <1.24,>=1.20, installed: 1.22]
bs4==0.0.1
  - beautifulsoup4 [required: Any, installed: 4.6.0]
celery-once==2.0.0
  - celery [required: Any, installed: 4.2.1]
    - billiard [required: >=3.5.0.2,<3.6.0, installed: 3.5.0.4]
    - kombu [required: <5.0,>=4.2.0, installed: 4.2.1]
      - amqp [required: >=2.1.4,<3.0, installed: 2.3.2]
        - vine [required: >=1.1.3, installed: 1.1.4]
    - pytz [required: >dev, installed: 2017.2]
  - redis [required: >=2.10.2, installed: 2.10.6]
certifi==2017.7.27.1
chardet==3.0.4
colorama==0.3.9
configparser==3.5.0
cryptography==2.3.1
  - asn1crypto [required: >=0.21.0, installed: 0.24.0]
  - cffi [required: !=1.11.3,>=1.7, installed: 1.11.5]
    - pycparser [required: Any, installed: 2.18]
  - idna [required: >=2.1, installed: 2.6]
  - six [required: >=1.4.1, installed: 1.10.0]
dj-static==0.0.6
  - static3 [required: Any, installed: 0.7.0]
django-celery-beat==1.1.1
  - celery [required: <5.0,>=4.0, installed: 4.2.1]
    - billiard [required: >=3.5.0.2,<3.6.0, installed: 3.5.0.4]
    - kombu [required: <5.0,>=4.2.0, installed: 4.2.1]
      - amqp [required: >=2.1.4,<3.0, installed: 2.3.2]
        - vine [required: >=1.1.3, installed: 1.1.4]
    - pytz [required: >dev, installed: 2017.2]
django-celery-results==1.0.1
  - celery [required: <5.0,>=4.0, installed: 4.2.1]
    - billiard [required: >=3.5.0.2,<3.6.0, installed: 3.5.0.4]
    - kombu [required: <5.0,>=4.2.0, installed: 4.2.1]
      - amqp [required: >=2.1.4,<3.0, installed: 2.3.2]
        - vine [required: >=1.1.3, installed: 1.1.4]
    - pytz [required: >dev, installed: 2017.2]
django-cors-headers==2.1.0
django-filter==1.1.0
django-heroku==0.3.1
  - dj-database-url [required: >=0.5.0, installed: 0.5.0]
  - django [required: Any, installed: 2.0.7]
    - pytz [required: Any, installed: 2017.2]
  - psycopg2 [required: Any, installed: 2.7.3.1]
  - whitenoise [required: Any, installed: 3.3.1]
django-timezone-field==3.0
  - django [required: >=1.8, installed: 2.0.7]
    - pytz [required: Any, installed: 2017.2]
  - pytz [required: Any, installed: 2017.2]
django-tools==0.36.0
  - Django [required: >=1.8, installed: 2.0.7]
    - pytz [required: Any, installed: 2017.2]
  - lxml [required: Any, installed: 4.1.1]
djangorestframework-recursive==0.1.2
  - Django [required: Any, installed: 2.0.7]
    - pytz [required: Any, installed: 2017.2]
  - djangorestframework [required: >=3.0, installed: 3.8.2]
drf-openapi==1.3.0
  - Click [required: >=6.0, installed: 6.7]
  - django-rest-swagger [required: ==2.1.2, installed: 2.1.2]
    - coreapi [required: >=2.3.0, installed: 2.3.3]
      - coreschema [required: Any, installed: 0.0.4]
        - jinja2 [required: Any, installed: 2.10]
          - MarkupSafe [required: >=0.23, installed: 1.0]
      - itypes [required: Any, installed: 1.1.0]
      - requests [required: Any, installed: 2.12.1]
      - uritemplate [required: Any, installed: 3.0.0]
    - djangorestframework [required: >=3.5.4, installed: 3.8.2]
    - openapi-codec [required: >=1.3.1, installed: 1.3.2]
      - coreapi [required: >=2.2.0, installed: 2.3.3]
        - coreschema [required: Any, installed: 0.0.4]
          - jinja2 [required: Any, installed: 2.10]
            - MarkupSafe [required: >=0.23, installed: 1.0]
        - itypes [required: Any, installed: 1.1.0]
        - requests [required: Any, installed: 2.12.1]
        - uritemplate [required: Any, installed: 3.0.0]
    - simplejson [required: Any, installed: 3.16.0]
drf-yasg==1.9.1
  - coreapi [required: >=2.3.3, installed: 2.3.3]
    - coreschema [required: Any, installed: 0.0.4]
      - jinja2 [required: Any, installed: 2.10]
        - MarkupSafe [required: >=0.23, installed: 1.0]
    - itypes [required: Any, installed: 1.1.0]
    - requests [required: Any, installed: 2.12.1]
    - uritemplate [required: Any, installed: 3.0.0]
  - coreschema [required: >=0.0.4, installed: 0.0.4]
    - jinja2 [required: Any, installed: 2.10]
      - MarkupSafe [required: >=0.23, installed: 1.0]
  - Django [required: >=1.11.7, installed: 2.0.7]
    - pytz [required: Any, installed: 2017.2]
  - djangorestframework [required: >=3.7.7, installed: 3.8.2]
  - future [required: >=0.16.0, installed: 0.16.0]
  - inflection [required: >=0.3.1, installed: 0.3.1]
  - openapi-codec [required: >=1.3.2, installed: 1.3.2]
    - coreapi [required: >=2.2.0, installed: 2.3.3]
      - coreschema [required: Any, installed: 0.0.4]
        - jinja2 [required: Any, installed: 2.10]
          - MarkupSafe [required: >=0.23, installed: 1.0]
      - itypes [required: Any, installed: 1.1.0]
      - requests [required: Any, installed: 2.12.1]
      - uritemplate [required: Any, installed: 3.0.0]
  - ruamel.yaml [required: >=0.15.34, installed: 0.15.42]
  - six [required: >=1.10.0, installed: 1.10.0]
  - uritemplate [required: >=3.0.0, installed: 3.0.0]
enum34==1.1.6
flex==6.13.2
  - click [required: >=3.3,<7, installed: 6.7]
  - jsonpointer [required: >=1.7,<2, installed: 1.14]
  - PyYAML [required: >=3.11,<4, installed: 3.13]
  - requests [required: <3,>=2.4.3, installed: 2.12.1]
  - rfc3987 [required: >=1.3.4,<2, installed: 1.3.7]
  - six [required: >=1.7.3,<2, installed: 1.10.0]
  - strict-rfc3339 [required: <1,>=0.7, installed: 0.7]
  - validate-email [required: >=1.2,<2, installed: 1.3]
googlemaps==3.0.2
  - requests [required: >=2.11.1,<3.0, installed: 2.12.1]
gunicorn==19.7.1
html-codec==1.0.0
  - coreapi [required: Any, installed: 2.3.3]
    - coreschema [required: Any, installed: 0.0.4]
      - jinja2 [required: Any, installed: 2.10]
        - MarkupSafe [required: >=0.23, installed: 1.0]
    - itypes [required: Any, installed: 1.1.0]
    - requests [required: Any, installed: 2.12.1]
    - uritemplate [required: Any, installed: 3.0.0]
  - jinja2 [required: Any, installed: 2.10]
    - MarkupSafe [required: >=0.23, installed: 1.0]
html-json-forms==1.0.0
Markdown==2.6.11
pip-review==1.0
  - packaging [required: Any, installed: 18.0]
    - pyparsing [required: >=2.0.2, installed: 2.2.2]
    - six [required: Any, installed: 1.10.0]
  - pip [required: Any, installed: 18.1]
psycopg2-binary==2.7.5
pylint==1.7.2
  - astroid [required: >=1.5.1, installed: 1.5.3]
    - lazy-object-proxy [required: Any, installed: 1.3.1]
    - six [required: Any, installed: 1.10.0]
    - wrapt [required: Any, installed: 1.10.11]
  - isort [required: >=4.2.5, installed: 4.2.15]
  - mccabe [required: Any, installed: 0.6.1]
  - six [required: Any, installed: 1.10.0]
PyMySQL==0.7.11
PyPDF2==1.26.0
python-crontab==2.3.5
  - python-dateutil [required: Any, installed: 2.7.3]
    - six [required: >=1.5, installed: 1.10.0]
reportlab==3.4.0
  - pillow [required: >=2.4.0, installed: 5.2.0]
  - pip [required: >=1.4.1, installed: 18.1]
  - setuptools [required: >=2.2, installed: 40.4.3]
sendgrid==5.3.0
  - python-http-client [required: >=3.0, installed: 3.0.0]
singledispatch==3.4.0.3
  - six [required: Any, installed: 1.10.0]
social-auth-app-django==2.1.0
  - six [required: Any, installed: 1.10.0]
  - social-auth-core [required: >=1.2.0, installed: 1.6.0]
    - defusedxml [required: >=0.5.0rc1, installed: 0.5.0]
    - oauthlib [required: >=1.0.3, installed: 2.0.6]
    - PyJWT [required: >=1.4.0, installed: 1.5.3]
    - python3-openid [required: >=3.0.10, installed: 3.1.0]
      - defusedxml [required: Any, installed: 0.5.0]
    - requests [required: >=2.9.1, installed: 2.12.1]
    - requests-oauthlib [required: >=0.6.1, installed: 0.8.0]
      - oauthlib [required: >=0.6.2, installed: 2.0.6]
      - requests [required: >=2.0.0, installed: 2.12.1]
    - six [required: >=1.10.0, installed: 1.10.0]
sodapy==1.4.3
  - future [required: ==0.16.0, installed: 0.16.0]
  - requests [required: ==2.12.1, installed: 2.12.1]
swagger-spec-validator==2.3.1
  - jsonschema [required: Any, installed: 2.6.0]
  - pyyaml [required: Any, installed: 3.13]
  - six [required: Any, installed: 1.10.0]
toml==0.9.4
typed-ast==1.1.0
virtualenv==16.0.0
virtualenv-clone==0.3.0

