FROM python:3.8.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /src

WORKDIR /src
COPY . /src
RUN source /etc/profile
RUN pip install -r requirements.txt
