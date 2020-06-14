#!/bin/sh
set -e

if [ -f ~/.profile ]; then
    source ~/.profile
fi

if [ "$#" -gt "0" ]; then
    if [ "$1" == "uwsgi" ]; then
        start=$(date +%s)

        python manage.py migrate --noinput
        python manage.py collectstatic --noinput --clear

        if [ ! -z "${SENTRY_AUTH_TOKEN}" -a ! -z "${SENTRY_ORG}" -a ! -e ~/.deployed ]; then
            name="DockerHubUpdateNotifier"
            version=$(cut -d'=' -f 2 < ./config/__init__.py | tr -d "' \r")
            echo "Version '${version}' deployment information is being sent to Sentry.io."

            /usr/local/bin/sentry_deploy.py "${name}@${version}" "${start}"

            touch ~/.deployed
        fi
    fi

    exec "$@"
fi
