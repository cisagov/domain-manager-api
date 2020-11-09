FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

WORKDIR /var/www/

ADD ./requirements.txt /var/www/requirements.txt
RUN pip install --upgrade pip \
    pip install -r requirements.txt

ADD ./src/ /var/www/

# Get certs for document db
RUN  wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem

# install hugo static site gen
RUN wget https://github.com/gohugoio/hugo/releases/download/v0.78.1/hugo_0.78.1_Linux-64bit.tar.gz

RUN mkdir /tmp/hugo
RUN tar -C /tmp/hugo -xzf hugo_0.78.1_Linux-64bit.tar.gz

ENV PATH "/tmp/hugo:${PATH}"
ENV PYTHONPATH "${PYTHONPATH}:/var/www"

# Entrypoint
COPY ./etc/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod a+x /usr/local/bin/entrypoint.sh

EXPOSE 5000
EXPOSE 80
EXPOSE 443

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
