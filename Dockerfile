FROM golang:1.18.4-alpine AS build

<<<<<<< HEAD
<<<<<<< HEAD
WORKDIR /src/
COPY /src/staticgen/ /src/
RUN CGO_ENABLED=0 GOOS=linux go build -o /bin/main
=======
FROM python:3.11.4-alpine
>>>>>>> 8c26a61517f4254b82bb73a78544145c62828a89
=======
FROM python:3.12.0-alpine
>>>>>>> 1ea8a3fa98e790d66f8d5e10375f73c5be4d5fd5

FROM python:3.10.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
    apt-get install -y python3-pip python-dev

WORKDIR /var/www/

ADD ./requirements.txt /var/www/requirements.txt
RUN pip install --upgrade pip \
    pip install -r requirements.txt

ADD ./src/ /var/www/

ENV PYTHONPATH "${PYTHONPATH}:/var/www"

# Get static gen build
COPY --from=build /bin/main /bin/main

# Entrypoint
COPY ./etc/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

EXPOSE 5000
EXPOSE 80
EXPOSE 443

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
