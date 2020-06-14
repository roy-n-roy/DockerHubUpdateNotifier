#!/usr/bin/env python

import argparse
import os
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlencode
from urllib.request import HTTPError, Request, urlopen

SENTRY_AUTH_TOKEN = os.getenv('SENTRY_AUTH_TOKEN')
SENTRY_ORG = os.getenv('SENTRY_ORG')
SENTRY_ENV = os.getenv('SENTRY_ENV', 'prod')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS')


if SENTRY_AUTH_TOKEN is None:
    print(
        'Error: Set your authentication token'
        ' to the \'SENTRY_AUTH_TOKEN\' environment variable')
    exit(1)

if SENTRY_ORG is None:
    print(
        'Error: Set your organization '
        'to the \'SENTRY_ORG\' environment variable')
    exit(1)

parser = argparse.ArgumentParser()
parser.add_argument("version")
parser.add_argument("starttime")
args = parser.parse_args()

data = {'environment': SENTRY_ENV}
if ALLOWED_HOSTS:
    data['url'] = 'https://' + ALLOWED_HOSTS.split(' ')[0].split(',')[0]

data['dateStarted'] = datetime.fromtimestamp(int(args.starttime), timezone.utc)

req = Request(
    f'https://sentry.io/api/0/organizations/{SENTRY_ORG}/releases/'
    f'{args.version}/deploys/',
    headers={'Authorization': f'Bearer {SENTRY_AUTH_TOKEN}'},
    method='POST',
    data=urlencode(data).encode('ascii')
)

try:
    with urlopen(req) as res:
        res.read().decode()
except HTTPError as e:
    print(e)
    print(f'  url  : {e.filename}\n  data : {parse_qs(req.data)}')
    exit(1)

print('Deployment to Sentry.io was successful.')
exit(0)
