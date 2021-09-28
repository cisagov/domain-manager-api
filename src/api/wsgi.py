"""Wsgi."""
# cisagov Libraries
from api.config import API_HOST, API_PORT
from api.main import app

if __name__ == "__main__":
    app.run(host=API_HOST, port=API_PORT)
