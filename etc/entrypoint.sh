#!/bin/bash

if [[ $DEBUG -eq 1 ]]
then
    echo "Debug Mode"
    flask run -h 0.0.0.0
else
    echo "Serve using WSGI"
    gunicorn --workers=$WORKERS --bind=0.0.0.0:5000 wsgi:app
fi
