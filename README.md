# pgif

This is description of pgif


## Table of Contents  
- [Installation](#Installation)  
- [Usage](#Usage)  



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




## Usage
<a name="Usage"/>
- Running Web Server
```shell
    $ python manage.py runserver
```
