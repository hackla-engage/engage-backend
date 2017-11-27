import os

def configure_overrides(settings):
    #this is the codeship environment
    if os.getlogin() == "rof":
        settings['DATABASES'].update(dict(
            {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': 'test',
                    'USER': os.environ.get('PGUSER'),
                    'PASSWORD':os.environ.get('PGPASSWORD'),
                    'HOST':'127.0.0.1',
                }
            }
        ))