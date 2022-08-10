#!/bin/bash

# run staticgen
echo "Launch static gen app"
/bin/main &

echo "Starting Domain Manager API"
# run flask
if [[ $FLASK_DEBUG -eq 1 ]]; then
  echo "Debug Mode"
  python api/wsgi.py
else
  echo "Serve using WSGI"
  gunicorn --workers="$WORKERS" --preload --bind=0.0.0.0:5000 --timeout=180 api.wsgi:app
fi
