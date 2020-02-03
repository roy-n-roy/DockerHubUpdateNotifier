FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add --no-cache gettext postgresql-libs linux-headers && apk add --virtual .build-deps gcc musl-dev postgresql-dev
RUN echo "export SECRET_KEY=\"\$(cat /dev/urandom | tr -dc 'a-zA-Z0-9%&@+\-*/=^~|' | fold -w 80 | head -n 1)\"" >> ~/.profile

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY django/ /app/

RUN django-admin compilemessages

EXPOSE 3031
CMD . ~/.profile && python manage.py migrate && uwsgi uwsgi.ini
