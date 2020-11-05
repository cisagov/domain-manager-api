FROM golang:1.15-alpine AS build

WORKDIR /hugo/
COPY  hugo/ /hugo/
RUN CGO_ENABLED=1 go install


FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

WORKDIR /var/www/

COPY --from=build /go/bin/hugo /var/www/hugo

ADD ./requirements.txt /var/www/requirements.txt
RUN pip install --upgrade pip \
    pip install -r requirements.txt

ADD ./src/ /var/www/

# Get certs for document db
RUN  wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem

# Entrypoint
COPY ./etc/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

EXPOSE 5000
EXPOSE 80
EXPOSE 443

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
