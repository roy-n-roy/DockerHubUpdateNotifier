FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN addgroup -g 1000 django \
 && adduser -S -u 1000 django -G django

RUN echo "export SECRET_KEY=\"\$(cat /dev/urandom | tr -dc 'a-zA-Z0-9%&@+\-*/=^~|' | fold -w 80 | head -n 1)\"" >> ~django/.profile

COPY requirements.txt .

RUN apk add --no-cache gettext postgresql-libs \
 && apk add --no-cache --virtual .build-deps gcc linux-headers musl-dev postgresql-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apk del --no-cache --purge .build-deps

COPY django/ /app/

RUN django-admin compilemessages

COPY entrypoint.sh /usr/local/bin/

ADD https://github.com/getsentry/sentry-cli/releases/latest/download/sentry-cli-Linux-x86_64 /usr/local/bin/sentry-cli
RUN chmod 755 /usr/local/bin/sentry-cli /usr/local/bin/entrypoint.sh

USER django

EXPOSE 3031
ENTRYPOINT [ "entrypoint.sh" ]
CMD [ "webapp" ]
