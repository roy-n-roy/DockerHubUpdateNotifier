#!/usr/bin/env python3
import argparse
import json
import logging
import smtplib
import sqlite3
import textwrap
import time
from email.mime.text import MIMEText
from email.utils import formatdate
from os import environ, path, remove

import requests
import schedule
from dateutil import parser

VERSION = '0.1.0'

DOCKER_HUB_REPO_TAGS_API_URL = 'https://hub.docker.com/v2/repositories/{0}/{1}/tags/{2}'

DB_DIR  = environ['DB_DIR'] if 'DB_DIR' in environ.keys() else path.sep + 'db'
DB_FILE = DB_DIR + path.sep + 'docker_repos.sqlite'

MAIL_FROM = environ['MAIL_FROM'] if 'MAIL_FROM' in environ.keys() else None
MAIL_PASS = environ['MAIL_PASS'] if 'MAIL_PASS' in environ.keys() else None
SMTP_HOST = environ['SMTP_HOST'] if 'SMTP_HOST' in environ.keys() else None
SMTP_PORT = environ['SMTP_PORT'] if 'SMTP_PORT' in environ.keys() else None

LOG_LEVEL = getattr(logging, environ['LOG_LEVEL'].upper(), None) if 'LOG_LEVEL' in environ.keys() else logging.INFO
LOG_LEVEL = LOG_LEVEL if isinstance(LOG_LEVEL, int) else logging.INFO

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=LOG_LEVEL)

def check_update():
	conn = sqlite3.connect(DB_FILE)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	for row in cur.execute('''
				SELECT users.user_id, repo.user, repo.name, repo.tag, repo.last_updated, users.mail_address
				FROM watching_repositories as repo INNER JOIN users ON repo.user_id=users.user_id
			'''):
		try:
			r = requests.get(DOCKER_HUB_REPO_TAGS_API_URL.format(row['user'], row['name'], row['tag']))
			r.raise_for_status()
			json = r.json()
		except:
			logging.exception("Failed to get repository last updated from Docker Hub.")
			continue
		if row[4] is None or row[4] != json['last_updated']:
			logging.info("'{0}/{1}:{2}' was updated.")
			try:
				conn.execute('UPDATE watching_repositories SET last_updated = ? WHERE user_id = ? and user = ? and name = ? and tag = ?',
						(json['last_updated'], row['user_id'], row['user'], row['name'], row['tag'])
					)
			except:
				logging.exception("DB UPDATE column 'last_updated' SQL Error.")
				continue

			try:
				notify_dest = conn.execute('SELECT mail_address, webhook_url FROM users WHERE user_id = ?', (row['user_id'], )).fetchone()
			except:
				logging.exception("DB SELECT notify destination SQL Error.")
				continue
			
			if notify_dest['mail_address'] is None and notify_dest['webhook_url'] is None:
				logging.warn("user_id {0} 's notify destination is empty.".format(row['user_id']))
				continue

			if notify_dest['mail_address'] is not None:
				if row['user'] == 'library':
					message_text = {"text": "{0}:{1} was updated on {2}.\nhttps://hub.docker.com/_/{0}".format(row['name'], row['tag'], parser.isoparse(json['last_updated']).strftime('%c'))}
				else:
					message_text = {"text": "{0}/{1}:{2} was updated on {3}.\nhttps://hub.docker.com/r/{0}/{1}".format(row['user'], row['name'], row['tag'], parser.isoparse(json['last_updated']).strftime('%c'))}

				try:
					send_email(notify_dest['mail_address'], message_text)
				except:
					logging.exception("Send e-mail Error.")
				else:
					logging.info('sent e-mail to user_id {0}'.format(row['user_id']))


			if notify_dest['webhook_url'] is not None:
				if row['user'] == 'library':
					post_json = {"text": "<https://hub.docker.com/_/{0}|{0}:{1}> was updated on {2}.".format(row['name'], row['tag'], parser.isoparse(json['last_updated']).strftime('%c'))}
				else:
					post_json = {"text": "<https://hub.docker.com/r/{0}/{1}|{0}/{1}:{2}> was updated on {3}.".format(row['user'], row['name'], row['tag'], parser.isoparse(json['last_updated']).strftime('%c'))}
				try:
					json = requests.post(notify_dest['webhook_url'], json=post_json)
					json.raise_for_status()
				except:
					logging.exception("Post webhook URL Error.")
				else:
					logging.info('posted webhook to user_id {0}'.format(row['user_id']))

		else:
			logging.debug("'{0}/{1}:{2}' was not updated.".format(row['user'], row['name'], row['tag']))

	if conn.in_transaction:
		conn.commit()

def send_email(to, message):
	if to is None or message is None:
		return

	if MAIL_FROM is None or MAIL_PASS is None or SMTP_HOST is None or SMTP_PORT is None:
		return
	
	msg = MIMEText(message)
	msg['To'] = to
	msg['Subject'] = 'Docker Hub Update Notify.'
	msg['From'] = MAIL_FROM
	msg['Date'] = formatdate()

	with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
		smtp.login(MAIL_FROM, MAIL_PASS)
		smtp.sendmail(MAIL_FROM, to, message.as_string())

def db_create():
	try:
		conn = sqlite3.connect(DB_FILE)
	except:
		logging.exception("DB connection Error. DB_FILE: {0}".format(DB_FILE))
		

	try:
		conn.executescript('''
				CREATE TABLE "users" (
					"user_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
					"mail_address"	TEXT,
					"webhook_url"	TEXT
				);
				CREATE TABLE "watching_repositories" (
					"user_id"	INTEGER NOT NULL,
					"user"	TEXT NOT NULL DEFAULT 'library',
					"name"	TEXT NOT NULL,
					"tag"	TEXT NOT NULL,
					"last_updated"	TEXT,
					PRIMARY KEY("user_id","user","name","tag"),
					FOREIGN KEY("user_id") REFERENCES "users"("user_id")
				);
			''')
		conn.commit()
	except:
		conn.close()
		logging.exception('DB CREATE tables Error.')
		remove(DB_FILE)
		raise

def run():
	check_update()
	schedule.every().hour.do(check_update)

	while True:
		schedule.run_pending()
		time.sleep(1)

def show_list():
	pass

def register_user(user_id:str, notify_dest:str):
	pass

def delete_user(user_id:str):
	pass

def subscribe_repository(user_id:str, repository_url:str):
	pass

def unsubscribe_repository(user_id:str, repository_url:str):
	pass

if __name__ == '__main__':
	argperser = argparse.ArgumentParser(description="Docker Hub Update Notifier.")
	argperser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
	argperser.add_argument('-l', '--list', help='show list of users and subscriptions.', action='store_true')
	argperser.add_argument('-r', '--register-user', help='registering a user with e-mail address or webhook URL or both.', metavar=('USER_ID', 'EMAIL_or_WEBHOOK'), nargs=2)
	argperser.add_argument('-d', '--delete-user', help='delete a user.', metavar=('USER_ID'), nargs=1)
	argperser.add_argument('-s', '--subscribe', help='subscribe to the Docker Hub repository.', metavar=('USER_ID','REPO_URL'), nargs=2)
	argperser.add_argument('-u', '--unsubscribe', help='unsubscribe to the Docker Hub repository.', metavar=('USER_ID','REPO_URL'), nargs=2)

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
