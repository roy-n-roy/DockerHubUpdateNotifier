import logging
import smtplib
import time
from email.mime.text import MIMEText
from email.utils import formatdate
from os import environ, path

import dataset
import requests
import schedule
from dataset.util import DatasetException
from dateutil import parser as dateparser
from requests.exceptions import RequestException

VERSION = '0.1.0'

DOCKER_HUB_API_URL = 'https://hub.docker.com/v2/repositories/{0}/{1}/tags/{2}'

DB_DIR = environ['DB_DIR'] if 'DB_DIR' in environ.keys() else path.sep + 'data'
DB_FILE = DB_DIR + path.sep + 'docker_repos.sqlite'

MAIL_FROM = environ['MAIL_FROM'] if 'MAIL_FROM' in environ.keys() else None
MAIL_PASS = environ['MAIL_PASS'] if 'MAIL_PASS' in environ.keys() else None
SMTP_HOST = environ['SMTP_HOST'] if 'SMTP_HOST' in environ.keys() else None
SMTP_PORT = environ['SMTP_PORT'] if 'SMTP_PORT' in environ.keys() else None

LOG_LEVEL = getattr(logging, environ['LOG_LEVEL'].upper(
), None) if 'LOG_LEVEL' in environ.keys() else logging.INFO
LOG_LEVEL = LOG_LEVEL if isinstance(LOG_LEVEL, int) else logging.INFO

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s', level=LOG_LEVEL)

SQL_SELECT_JOIN = '''\
SELECT * FROM watching_repositories INNER JOIN users USING(user_seq)\
'''


def check_update():
    db = get_db()
    for row in db.query(SQL_SELECT_JOIN):
        try:
            url = DOCKER_HUB_API_URL.format(
                row['publisher'], row['repo_name'], row['repo_tag'])
            r = requests.get(url)
            r.raise_for_status()
            json = r.json()
        except RequestException:
            logging.exception(
                " Failed to get repository last updated from Docker Hub.")
            continue

        if row['last_updated'] is not None and \
                row['last_updated'] == json['last_updated']:
            logging.debug(
                " '{0}/{1}:{2}' was not updated."
                .format(row['publisher'], row['repo_name'], row['repo_tag']))
            continue

        logging.info(
            "'{0}/{1}:{2}' was updated."
            .format(row['publisher'], row['repo_name'], row['repo_tag']))

        db.begin()
        try:
            keys = ['user_seq', 'publisher', 'repo_name', 'repo_tag']
            data = {k: v for k, v in row.items() if k in keys}
            data['last_updated'] = json['last_updated']
            db['watching_repositories'].update(data, keys)
        except DatasetException:
            logging.exception(
                " DB UPDATE column 'last_updated' SQL Error.")
            if db.in_transaction:
                db.rollback()
                logging.debug(" DB Rollbacked.")
            continue

        try:
            notify_dest = db['users'].find_one(user_seq=row['user_seq'])
        except DatasetException:
            logging.exception(
                " DB SELECT notify destination SQL Error.")
            continue

        if not notify_dest['mail_address'] and \
                not notify_dest['webhook_url']:
            logging.warn(
                " user_seq {0} 's notify destination is empty."
                .format(row['user_seq']))
            if db.in_transaction:
                db.rollback()
                logging.debug(" DB Rollbacked.")
            continue

        updated = dateparser.isoparse(json['last_updated']).strftime('%c')
        if row['publisher'] == 'library':
            repo_text = "{0}:{1}".format(row['repo_name'], row['repo_tag'])
            repo_url = "https://hub.docker.com/_/{0}".format(
                row['repo_name']
            )
        else:
            repo_text = "{0}/{1}:{2}".format(
                row['publisher'], row['repo_name'], row['repo_tag']
            )
            repo_url = "https://hub.docker.com/r/{0}/{1}".format(
                row['publisher'], row['repo_name']
            )

        if notify_dest['mail_address']:
            message_text = (
                "{0} was updated on {2}.\n{1}"
                .format(repo_text, repo_url, updated)
            )

            try:
                send_email(notify_dest['mail_address'], message_text)
            except smtplib.SMTPException:
                logging.exception(
                    " Send e-mail Error.")
                if db.in_transaction:
                    db.rollback()
                    logging.debug(" DB Rollbacked.")
            else:
                logging.info(
                    " sent e-mail to user_seq {0}"
                    .format(row['user_seq']))

        if notify_dest['webhook_url']:
            post_json = {
                "text":
                "<{1}|{0}> was updated on {2}."
                .format(repo_text, repo_url, updated)
            }

            try:
                json = requests.post(
                    notify_dest['webhook_url'], json=post_json)
                json.raise_for_status()
            except RequestException:
                logging.exception("Post webhook URL Error.")
                if db.in_transaction:
                    db.rollback()
                    logging.debug(" DB Rollbacked.")
            else:
                logging.info(
                    " posted webhook to user_seq {0}"
                    .format(row['user_seq']))

        if db.in_transaction:
            db.commit()


def send_email(to, message):
    if to is None or message is None:
        return

    if SMTP_HOST is None or SMTP_PORT is None:
        logging.error(
            " environment variable 'SMTP_HOST', 'SMTP_PORT' is not set.")
        return
    elif MAIL_FROM is None or MAIL_PASS is None:
        logging.error(
            " environment variable 'MAIL_FROM', 'MAIL_PASS' is not set.")
        return

    msg = MIMEText(message)
    msg['To'] = to
    msg['Subject'] = 'Docker Hub Update Notify.'
    msg['From'] = MAIL_FROM
    msg['Date'] = formatdate()

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
        smtp.login(MAIL_FROM, MAIL_PASS)
        smtp.sendmail(MAIL_FROM, to, message.as_string())


def get_db() -> dataset.Database:
    try:
        return dataset.connect('sqlite:///' + DB_FILE)
    except DatasetException:
        logging.exception(
            " DB connection Error. DB_FILE: {0}"
            .format(DB_FILE))
        raise


def db_create():
    db = get_db()
    try:
        db.query('''
            CREATE TABLE "users" (
                "user_seq"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                "user_id"	TEXT NOT NULL UNIQUE,
                "mail_address"	TEXT,
                "webhook_url"	TEXT,
                "timezone"	TEXT
            );
        ''')
        db.query('''
            CREATE TABLE "watching_repositories" (
                "user_seq"	INTEGER NOT NULL,
                "publisher"	TEXT NOT NULL DEFAULT 'library',
                "repo_name"	TEXT NOT NULL,
                "repo_tag"	TEXT NOT NULL,
                "last_updated"	TEXT,
                PRIMARY KEY("user_seq","publisher","repo_name","repo_tag"),
                FOREIGN KEY("user_seq") REFERENCES "users"("user_seq")
            );
        ''')
    except DatasetException:
        logging.exception(' DB CREATE tables Error.')
        raise


if __name__ == '__main__':
    if not path.exists(DB_FILE):
        db_create()

    check_update()
    schedule.every().hour.do(check_update)

    while True:
        schedule.run_pending()
        time.sleep(1)
