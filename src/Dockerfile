FROM python:3.9.19
ENV PYTHONUNBUFFERED 1
RUN mkdir /src

WORKDIR /src
COPY . /src
RUN make init
