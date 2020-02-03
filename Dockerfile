FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN echo "export SECRET_KEY=\"\$(cat /dev/urandom | tr -dc 'a-zA-Z0-9%&@+\-*/=^~|' | fold -w 80 | head -n 1)\"" >> ~/.profile
RUN apk add --no-cache gettext postgresql-libs

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc linux-headers musl-dev postgresql-dev && pip install --no-cache-dir -r requirements.txt && apk del --no-cache .build-deps

COPY django/ /app/

RUN django-admin compilemessages

EXPOSE 3031
CMD . ~/.profile && python manage.py migrate && python manage.py collectstatic && uwsgi uwsgi.ini
