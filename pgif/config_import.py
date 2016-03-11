import os

try:
    # environment = os.environ['APP_ENV']
    environment = 'development'
    if str(environment) in 'development testing':
        from .config_dev import *
    elif str(environment) in 'staging production':
        from .config_production import *
except KeyError:
    raise KeyError('Enviroment Variable `APP_ENV` not set')
