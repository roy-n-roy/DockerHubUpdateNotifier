#!/bin/sh
set -e

if [ -f ~/.profile ]; then
    source ~/.profile
fi

if [ "$#" -gt "0" ]; then
    if [ "$1" == "webapp" ]; then
        start=$(date +%s)

        python manage.py migrate --noinput
        python manage.py collectstatic --noinput --clear

        end=$(date +%s)

        if [ ! -z "${SENTRY_AUTH_TOKEN}" -a ! -z "${SENTRY_ORG}" -a ! -e ~/.deployed ]; then
            version=$(cut -d'=' -f 2 < ./config/__init__.py | tr -d "' \r")
            echo "Version ${version} deployment information is being sent to Sentry."
            sentry-cli releases deploys "DockerHubUpdateNotifier@${version}" new -e "${SENTRY_ENV:-prod}" -t $((end-start))
            touch ~/.deployed
        fi

        exec uwsgi uwsgi.ini

    elif [ "$1" == "batch" ]; then
        exec python scheduler.py batch

    else
        exec "$@"
    fi
fi
