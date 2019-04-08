FROM python:alpine3.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /MassEnergizeApp;
WORKDIR /MassEnergizeApp

ADD requirements.txt /MassEnergizeApp
RUN pip install -r /MassEnergizeApp/requirements.txt

# Install bash
RUN apk add --no-cache bash gawk sed grep bc coreutils