#!/bin/bash

# run staticgen
echo "Launch static gen app"
/bin/main &

echo "Starting Domain Manager API"
# run flask
if [[ $DEBUG -eq 1 ]]
then
  echo "Debug Mode"
  flask run -h 0.0.0.0
else
  echo "Serve using WSGI"
  gunicorn --workers="$WORKERS" --bind=0.0.0.0:5000 --timeout=180 api.wsgi:app
fi
