<<<<<<< HEAD
FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

WORKDIR /var/www/

ADD ./requirements.txt /var/www/requirements.txt
RUN pip install -r requirements.txt

ADD . /var/www/

EXPOSE 5000

CMD ["flask", "run", "-h", "0.0.0.0"]
=======
FROM lambci/lambda:build-python3.8
LABEL maintainer="mark.feldhousen@trio.dhs.gov"
LABEL vendor="Cyber and Infrastructure Security Agency"

COPY build.sh .

# Files needed to install local eal module
COPY setup.py .
COPY requirements.txt .
COPY README.md .
COPY eal ./eal

COPY lambda_handler.py .

ENTRYPOINT ["./build.sh"]
>>>>>>> develop
