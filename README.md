# pgif

Convert video to Gif.

## Table of Contents  
- [Requirements](#Requirements)  
- [Installation](#Installation)  
- [Usage](#Usage)  
- [Troubleshooting](#Troubleshooting)  
- [Sass Command](#SassCommand)  


<a name="Requirements"/>
## Requirements
- Django 1.9.4
- Django Rest Framework
- Mysql
- Gevent
- ffmpeg
- Cloudinary

<a name="Installation"/>
## Installation
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

- GIF Clound
```shell
    $ pip install cloudinary
```


<a name="Usage"/>
## Usage
- Uwsgi Config
```shell
[uwsgi]
chdir = /var/www/html/pgif
home = /root/.pgif
module = pgif.wsgi:application

uid = root
gid = www-data

master = true
processes = 5

socket = /tmp/pgif.sock
chmod-socket = 664
vacuum = true
```

- Nginx Config
```shell
server {
    listen 80;
    server_name localhost;
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/pgif.sock;
    }
}
```

<a name="Troubleshooting"/>
## Troubleshooting

- 413 Request Entity Too Large
```html
    edit nginx configuration (/etc/nginx/nginx.conf)
    inside http section
    change client_max_body_size 1m; to client_max_body_size 100M;
```

- 502 Bad Gateway
```html
   make sure the UWsgi services runing well
```

- Nginx Configuration
```shell
server {
    listen 80;
    server_name 127.0.0.1;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /vagrant/pgif/convert;
    }

    location /files/ {
        root /vagrant/files/;
    }

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/pgif.sock;
    }
}
```

<a name="SassCommand"/>
## Sass Command
```shell
$ sass --watch sass/index.scss:css/index.css --no-cache --sourcemap=none --style compressed
```
