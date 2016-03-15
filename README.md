# pgif

This is description of pgif


## Table of Contents  
- [Requirements](#Requirements)  
- [Installation](#Installation)  
- [Usage](#Usage)  

## Requirements
<a name="Requirements"/>
- Django 1.9.4
- Django Rest Framework
- Mysql
- Gevent
- ffmpeg


## Installation
<a name="Installation"/>
- VirtualEnv
```shell
    $ virtualenv -p python3 env
```

- Django 1.9.4
```shell
    $ pip install django
    $ django-admin startproject pgif .
```

- Django Rest Framework
```shell
    $ pip install djangorestframework
    $ pip install markdown       # Markdown support for the browsable API.
    $ pip install django-filter  # Filtering support
    $ pip install django-rest-swagger # An API documentation generator for Swagger UI and Django REST Framework version 2.3.8+
```

- Mysql
```shell
    $ sudo apt-get install python3-dev libmysqlclient-dev
    $ pip install mysqlclient
```

- Gevent
```shell
    $ pip install wheel
    $ pip install setuptools 'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent
```

- ffmpeg
```shell
    $ sudo add-apt-repository ppa:mc3man/trusty-media
    $ sudo apt-get update
    $ sudo apt-get dist-upgrade
    $ sudo apt-get install ffmpeg
```





## Usage
<a name="Usage"/>
- Running Web Server
```shell
    $ python manage.py runserver
```
