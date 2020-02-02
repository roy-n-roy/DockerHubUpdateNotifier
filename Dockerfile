FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add --no-cache gettext postgresql-libs linux-headers && apk add --virtual .build-deps gcc musl-dev postgresql-dev

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY django/ /app/

RUN django-admin compilemessages

EXPOSE 3031
CMD export SECRET_KEY="`cat /dev/urandom | tr -dc 'a-zA-Z0-9%&@+\-*/=^~|' | fold -w 80 | head -n 1`" && python manage.py migrate && uwsgi uwsgi.ini
