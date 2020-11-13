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
    fi

    exec "$@"
fi
