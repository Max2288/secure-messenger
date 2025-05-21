#!/usr/bin/env bash
if [[ $DEBUG != "True" ]];
  then
    exec gunicorn --workers 5 --preload --bind 0.0.0.0:1024 food.wsgi
  else
    exec python3 ./manage.py runserver 0.0.0.0:1024
fi;