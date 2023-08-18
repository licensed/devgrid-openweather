FROM python:3.9

RUN mkdir -p /opt/app/

WORKDIR /opt/app/

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .