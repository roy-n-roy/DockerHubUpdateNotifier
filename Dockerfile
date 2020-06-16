FROM python:3.8-alpine AS poetry

WORKDIR /tmp/poetry

RUN apk add --no-cache curl \
 && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

COPY pyproject.toml poetry.lock /tmp/poetry/

RUN source $HOME/.poetry/env \
 && poetry self update \
 && poetry export -f requirements.txt -E production -o /tmp/poetry/requirements.txt

FROM python:3.8-alpine AS django

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN addgroup -g 1000 django \
 && adduser -S -u 1000 django -G django \
 && echo "if [ ! \"\$SECRET_KEY\" ]; then export SECRET_KEY=\"\$(cat /dev/urandom | tr -dc 'a-zA-Z0-9%&@+\-*/=^~|' | fold -w 80 | head -n 1)\"; fi" >> ~django/.profile

RUN mkdir -p /static /var/run/django \
 && chown django:django /static /var/run/django

COPY --from=poetry /tmp/poetry/requirements.txt .

RUN apk add --no-cache postgresql-libs \
 && apk add --no-cache --virtual .build-deps gcc linux-headers musl-dev postgresql-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apk del --no-cache --purge .build-deps

COPY django/ /app/

RUN apk add --no-cache gettext \
 && django-admin compilemessages \
 && apk del --no-cache --purge gettext

COPY scripts /usr/local/bin

RUN chmod 755 /usr/local/bin/entrypoint.sh /usr/local/bin/sentry_deploy.py

USER django

ENTRYPOINT [ "entrypoint.sh" ]
CMD [ "uwsgi", "uwsgi.ini" ]
