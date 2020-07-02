# syntax = docker/dockerfile:experimental

FROM python:3.8-alpine AS poetry

WORKDIR /poetry

RUN apk add --no-cache curl \
 && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

COPY pyproject.toml poetry.lock /poetry/

RUN source $HOME/.poetry/env \
 && poetry self update \
 && poetry export -f requirements.txt -E production -o /poetry/requirements.txt


FROM python:3.8-alpine AS build_wheel

WORKDIR /build

COPY --from=poetry /poetry/requirements.txt .

RUN apk add --no-cache gcc linux-headers musl-dev postgresql-dev

RUN mkdir -p /build/wheel \
 && pip wheel -r requirements.txt -w /build/wheel


FROM python:3.8-alpine AS django

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN addgroup -g 1000 django \
 && adduser -S -u 1000 django -G django \
 && echo "if [ ! \"\$SECRET_KEY\" ]; then export SECRET_KEY=\"\$(cat /dev/urandom | tr -dc 'a-zA-Z0-9%&@+\-*/=^~|' | fold -w 80 | head -n 1)\"; fi" >> ~django/.profile

RUN mkdir -p /static /var/run/django \
 && chown django:django /static /var/run/django

RUN --mount=type=bind,from=build_wheel,source=/build/wheel,target=/wheel \
    apk add --no-cache postgresql-libs \
 && pip install --no-cache-dir /wheel/*.whl

COPY django/ /app/

RUN apk add --no-cache gettext \
 && django-admin compilemessages \
 && apk del --no-cache --purge gettext

COPY scripts /usr/local/bin

RUN chmod 755 /usr/local/bin/entrypoint.sh /usr/local/bin/sentry_deploy.py

USER django

ENTRYPOINT [ "entrypoint.sh" ]
CMD [ "uwsgi", "uwsgi.ini" ]
