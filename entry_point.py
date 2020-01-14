import argparse
import json
import logging
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.utils import formatdate
from os import path

import dataset
import requests
import schedule
from dateutil import parser
from urllib3.util import parse_url

VERSION = '0.1.0'

DOCKER_HUB_REPO_TAGS_API_URL = 'https://hub.docker.com/v2/repositories/{0}/{1}/tags/{2}'

DB_DIR  = os.environ['DB_DIR'] if 'DB_DIR' in os.environ.keys() else path.sep + 'db'
DB_FILE = DB_DIR + path.sep + 'docker_repos.sqlite'

MAIL_FROM = os.environ['MAIL_FROM'] if 'MAIL_FROM' in os.environ.keys() else None
MAIL_PASS = os.environ['MAIL_PASS'] if 'MAIL_PASS' in os.environ.keys() else None
SMTP_HOST = os.environ['SMTP_HOST'] if 'SMTP_HOST' in os.environ.keys() else None
SMTP_PORT = os.environ['SMTP_PORT'] if 'SMTP_PORT' in os.environ.keys() else None

LOG_LEVEL = getattr(logging, os.environ['LOG_LEVEL'].upper(), None) if 'LOG_LEVEL' in os.environ.keys() else logging.INFO
LOG_LEVEL = LOG_LEVEL if isinstance(LOG_LEVEL, int) else logging.INFO

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=LOG_LEVEL)

def check_update():
    db = get_db()
    db.begin()
    for row in db.query('SELECT * FROM watching_repositories INNER JOIN users USING(user_seq)'):
        try:
            r = requests.get(DOCKER_HUB_REPO_TAGS_API_URL.format(row['publisher'], row['repo_name'], row['repo_tag']))
            r.raise_for_status()
            json = r.json()
        except:
            logging.exception(" Failed to get repository last updated from Docker Hub.")
            continue

        if row['last_updated'] is None or row['last_updated'] != json['last_updated']:
            logging.info("'{0}/{1}:{2}' was updated.".format(row['publisher'], row['repo_name'], row['repo_tag']))
            try:
                keys = ['user_seq', 'publisher', 'repo_name', 'repo_tag']
                data = {k: v for k, v in row.items() if k in keys}
                data['last_updated'] = json['last_updated']
                db['watching_repositories'].update(data, keys)
            except:
                logging.exception(" DB UPDATE column 'last_updated' SQL Error.")
                continue

            try:
                notify_dest = db['users'].find_one(user_seq=row['user_seq'])
            except:
                logging.exception(" DB SELECT notify destination SQL Error.")
                continue

            if notify_dest['mail_address'] is None and notify_dest['webhook_url'] is None:
                logging.warn(" user_seq {0} 's notify destination is empty.".format(row['user_seq']))
                continue

            if notify_dest['mail_address'] is not None and notify_dest['mail_address'] != '':
                if row['publisher'] == 'library':
                    message_text = {"text": "{0}:{1} was updated on {2}.\nhttps://hub.docker.com/_/{0}".format(row['repo_name'], row['repo_tag'], parser.isoparse(json['last_updated']).strftime('%c'))}
                else:
                    message_text = {"text": "{0}/{1}:{2} was updated on {3}.\nhttps://hub.docker.com/r/{0}/{1}".format(row['publisher'], row['repo_name'], row['repo_tag'], parser.isoparse(json['last_updated']).strftime('%c'))}

                try:
                    send_email(notify_dest['mail_address'], message_text)
                except:
                    logging.exception(" Send e-mail Error.")
                else:
                    logging.info(" sent e-mail to user_seq {0}".format(row['user_seq']))

            if notify_dest['webhook_url'] is not None and notify_dest['webhook_url'] != '':
                if row['publisher'] == 'library':
                    post_json = {"text": "<https://hub.docker.com/_/{0}|{0}:{1}> was updated on {2}.".format(row['repo_name'], row['repo_tag'], parser.isoparse(json['last_updated']).strftime('%c'))}
                else:
                    post_json = {"text": "<https://hub.docker.com/r/{0}/{1}|{0}/{1}:{2}> was updated on {3}.".format(row['publisher'], row['repo_name'], row['repo_tag'], parser.isoparse(json['last_updated']).strftime('%c'))}

                try:
                    json = requests.post(notify_dest['webhook_url'], json=post_json)
                    json.raise_for_status()
                except:
                    logging.exception("Post webhook URL Error.")
                else:
                    logging.info(" posted webhook to user_seq {0}".format(row['user_seq']))

        else:
            logging.debug(" '{0}/{1}:{2}' was not updated.".format(row['publisher'], row['repo_name'], row['repo_tag']))

    if db.in_transaction:
        db.commit()

def send_email(to, message):
    if to is None or message is None:
        return

    if SMTP_HOST is None or SMTP_PORT is None:
        logging.error(" environment variable 'SMTP_HOST', 'SMTP_PORT' is not set.")
        return
    elif MAIL_FROM is None or MAIL_PASS is None:
        logging.error(" environment variable 'MAIL_FROM', 'MAIL_PASS' is not set.")
        return

    msg = MIMEText(message)
    msg['To'] = to
    msg['Subject'] = 'Docker Hub Update Notify.'
    msg['From'] = MAIL_FROM
    msg['Date'] = formatdate()

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.login(MAIL_FROM, MAIL_PASS)
            smtp.sendmail(MAIL_FROM, to, message.as_string())
    except:
        logging.exception(" send e-mail error.")

def get_db() -> dataset.Database:
    try:
        return dataset.connect('sqlite:///' + DB_FILE)
    except:
        logging.exception(" DB connection Error. DB_FILE: {0}".format(DB_FILE))
        raise

def db_create():
    db = get_db()
    try:
        db.query('''
                CREATE TABLE "users" (
                    "user_seq"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    "user_id"	TEXT NOT NULL UNIQUE,
                    "mail_address"	TEXT,
                    "webhook_url"	TEXT
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
    except:
        logging.exception(' DB CREATE tables Error.')
        raise

def run():
    check_update()
    schedule.every().hour.do(check_update)

    while True:
        schedule.run_pending()
        time.sleep(1)

def show_list():
    db = get_db()
    result = ['user_id,\trepository,\tlast update']
    try:
        for row in db.query('SELECT * FROM watching_repositories INNER JOIN users USING(user_seq)'):
            result.append("{0},\t{1}{2}:{3},\t{4}".format(row['user_id'], row['publisher'] + '/' if row['publisher'] != 'library' else '', row['repo_name'], row['repo_tag'], row['last_updated']))
    except:
        logging.exception(' DB SELECT tables Error.')

    print(os.linesep.join(result))

def register_user(user_id:str, notify_dest:str):
    with get_db() as db:
        if db['users'].count(user_id=user_id) != 0:
            logging.error(" user_id: {0} is already used.".format(user_id))
            return

        if '@' in notify_dest:
            email_add = notify_dest
            webhook_url = None
        elif parse_url(notify_dest).scheme is not None and parse_url(notify_dest).scheme in ['http', 'https']:
            email_add = None
            webhook_url = notify_dest
        else:
            logging.error(" user_id: {0} is already used.".format(user_id))
            return

        db['users'].insert(dict(user_id=user_id, mail_address=email_add, webhook_url=webhook_url))

def delete_user(user_id:str):
    with get_db() as db:
        if db['users'].count(user_id=user_id) == 0:
            logging.error(" user_id: {0} is not found.".format(user_id))
            return

        db['users'].delete(user_id=user_id)
        logging.debug(" user_id: {0} is deleted.".format(user_id))

def subscribe_repository(user_id:str, repo:str):
    publisher = repo.split('/')[0] if '/' in repo else 'library'
    repo_name = repo.split('/')[1] if '/' in repo else repo.split(':')[0] if repo in ':' else repo
    repo_tag  = repo.split(':')[1] if ':' in repo else 'latest'
    try:
        r = requests.get(DOCKER_HUB_REPO_TAGS_API_URL.format(publisher, repo_name, repo_tag))
        r.raise_for_status()
        json = r.json()
    except:
        logging.error(" {0} is not found on docker hub.".format(repo))
        return
    else:
        with get_db() as db:
            user = db['users'].find_one(user_id=user_id)
            if user is None or user['user_seq'] is None:
                logging.error("user_id: {0} is not found.".format(user_id))
                return
            if db['watching_repositories'].count(user_seq=user['user_seq'], publisher=publisher, repo_name=repo_name, repo_tag=repo_tag) != 0:
                logging.error(" {0} is already subscribed.")
                return

            try:
                db['watching_repositories'].insert(dict(user_seq=user['user_seq'], publisher=publisher, repo_name=repo_name, repo_tag=repo_tag, last_updated=json['last_updated']))
            except:
                logging.exception(" DB INSERT Error.")

def unsubscribe_repository(user_id:str, repo:str):
    publisher = repo.split('/')[0] if '/' in repo else 'library'
    repo_name = repo.split('/')[1] if '/' in repo else repo.split(':')[0] if repo in ':' else repo
    repo_tag  = repo.split(':')[1] if ':' in repo else 'latest'

    with get_db() as db:
        user = db['users'].find_one(user_id=user_id)
        if user is None or user['user_seq'] is None:
            logging.error(" user_id: {0} is not found.".format(user_id))
            return
        if db['watching_repositories'].count(user_seq=user['user_seq'], publisher=publisher, repo_name=repo_name, repo_tag=repo_tag) == 0:
            logging.error(" {0} i hasn't been subscribed yet.")
            return

        try:
            db['watching_repositories'].delete(user_seq=user['user_seq'], publisher=publisher, repo_name=repo_name, repo_tag=repo_tag)
        except:
            logging.exception(" DB DELETE Error.")

if __name__ == '__main__':
    argperser = argparse.ArgumentParser(description="Docker Hub Update Notifier.")
    argperser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
    argperser.add_argument('-l', '--list', help='show list of users and subscriptions.', action='store_true')
    argperser.add_argument('-r', '--register-user', help='registering a user with e-mail address or webhook URL.', metavar=('USER_ID', 'EMAIL_or_WEBHOOK'), nargs=2)
    argperser.add_argument('-d', '--delete-user', help='delete a user.', metavar=('USER_ID'), nargs=1)
    argperser.add_argument('-s', '--subscribe', help='subscribe to the Docker Hub repository.', metavar=('USER_ID','REPO:TAG'), nargs=2)
    argperser.add_argument('-u', '--unsubscribe', help='unsubscribe to the Docker Hub repository.', metavar=('USER_ID','REPO:TAG'), nargs=2)

    args = argperser.parse_args()

    if not path.exists(DB_FILE):
        db_create()

    if args.list:
        show_list()
    elif args.register_user:
        register_user(*args.register_user)
    elif args.delete_user:
        delete_user(*args.delete_user)
    elif args.subscribe:
        subscribe_repository(*args.subscribe)
    elif args.unsubscribe:
        unsubscribe_repository(*args.unsubscribe)
    else:
        run()
