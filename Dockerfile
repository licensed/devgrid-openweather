FROM python:3.9

WORKDIR /opt/app/

COPY . /opt/app/

RUN pip install -r requirements.txt

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "src.app.app:app", "--reload" ]
EXPOSE 8000