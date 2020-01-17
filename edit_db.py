#! /usr/bin/env python
import argparse
import logging
import re
import textwrap

import requests
from dataset.util import DatasetException
from dateutil import parser as dateparser
from dateutil import tz
from tabulate import tabulate
from email_validator import validate_email, EmailNotValidError

import tzlocal
from entry_point import DOCKER_HUB_API_URL, SQL_SELECT_JOIN, VERSION, get_db


def show_list():
    db = get_db()
    user_header = ['user id', 'e-mail address', 'webhook url']
    user_table = []
    repo_header = ['user id', 'repository', 'last update']
    repo_table = []
    try:
        for row in db.query(SQL_SELECT_JOIN):
            if row['publisher'] == 'library':
                repo_text = "{0}:{1}".format(row['repo_name'], row['repo_tag'])
            else:
                repo_text = "{0}/{1}:{2}".format(
                    row['publisher'], row['repo_name'], row['repo_tag']
                )

            repo_table.append([
                row['user_id'],
                repo_text,
                dateparser.isoparse(row['last_updated'])
                .astimezone(tz=tz.gettz(row['timezone']))
                .strftime('%c')
            ])
        for row in db['users'].find():
            user_table.append([
                row['user_id'],
                row['mail_address'],
                row['webhook_url']
            ])
    except DatasetException:
        logging.exception(' DB SELECT tables Error.')

    print(textwrap.dedent('''
        - Users:
        {0}


        - Repositories:
        {1}
        ''').format(
            tabulate(user_table, headers=user_header),
            tabulate(repo_table, headers=repo_header)
        )
    )


def register_user(user_id: str, notify_dest: str):
    url_pattern = r"https?://hooks\.slack\.com/services/"
    try:
        with get_db() as db:
            if db['users'].count(user_id=user_id) != 0:
                logging.error(" user_id: {0} is already used.".format(user_id))
                return

            if re.match(url_pattern, notify_dest):
                email_add = None
                webhook_url = notify_dest
            else:
                try:
                    email_add = validate_email(notify_dest)['email']
                    webhook_url = None
                except EmailNotValidError:
                    logging.error(
                        " {0}  is not a valid email address or webhook URL."
                        .format(user_id)
                        )
                    return

            db['users'].insert(dict(
                user_id=user_id,
                mail_address=email_add,
                webhook_url=webhook_url,
                timezone=tzlocal.get_localzone().zone
            ))
    except DatasetException:
        logging.exception(' DB Error.')


def delete_user(user_id: str):
    try:
        with get_db() as db:
            if db['users'].count(user_id=user_id) == 0:
                logging.error(" user_id: {0} is not found.".format(user_id))
                return

            # delete user's repositories.
            db['watching_repositories'].delete(
                user_seq=db['users'].find_one(user_id=user_id)['user_seq']
            )
            # delete user
            db['users'].delete(user_id=user_id)
            logging.debug(" user_id: {0} is deleted.".format(user_id))
    except DatasetException:
        logging.exception(' DB Error.')


def get_repo_id(repo: str) -> dict:
    if not repo or not isinstance(repo, str):
        return None

    publisher = repo.split('/')[0] if '/' in repo else 'library'
    repo_tag = repo.split(':')[1] if ':' in repo else 'latest'
    repo_name = (set(re.split(r'/|:', repo)) - {publisher, repo_tag}).pop()

    return dict(publisher=publisher, repo_name=repo_name, repo_tag=repo_tag)


def subscribe_repository(user_id: str, repo: str):
    repo_id = get_repo_id(repo)
    try:
        r = requests.get(DOCKER_HUB_API_URL.format(*repo_id.values()))
        r.raise_for_status()
        json = r.json()
    except requests.RequestException:
        logging.error(
            " {0}/{1}:{2} is not found on docker hub."
            .format(*repo_id.values())
        )
        return
    else:
        with get_db() as db:
            user = db['users'].find_one(user_id=user_id)
            if user is None or user['user_seq'] is None:
                logging.error("user_id: {0} is not found.".format(user_id))
                return

            keys = dict(user_seq=user['user_seq'], **repo_id)
            if db['watching_repositories'].count(**keys) != 0:
                logging.error(
                    " {0}/{1}:{2} is already subscribed."
                    .format(*repo_id.values())
                )
                return

            try:
                keys['last_updated'] = json['last_updated']
                db['watching_repositories'].insert(keys)
            except DatasetException:
                logging.exception(" DB INSERT Error.")


def unsubscribe_repository(user_id: str, repo: str):
    repo_id = get_repo_id(repo)

    with get_db() as db:
        user = db['users'].find_one(user_id=user_id)
        if user is None or user['user_seq'] is None:
            logging.error(" user_id: {0} is not found.".format(user_id))
            return

        keys = dict(user_seq=user['user_seq'], **repo_id)
        if db['watching_repositories'].count(**keys) == 0:
            logging.error(" {0} i hasn't been subscribed yet.")
            return

        try:
            db['watching_repositories'].delete(**keys)
        except DatasetException:
            logging.exception(" DB DELETE Error.")


if __name__ == '__main__':
    perser = argparse.ArgumentParser(
        description="Docker Hub Update Notifier.")
    perser.add_argument(
        '-v', '--version', action='version', version='%(prog)s ' + VERSION
    )
    grp = perser.add_mutually_exclusive_group()
    grp.add_argument(
        '-l', '--list', action='store_true',
        help='show list of users and subscriptions.'
    )
    grp.add_argument(
        '-r', '--register-user',
        metavar=('USER_ID', 'EMAIL_or_WEBHOOK'), nargs=2,
        help='registering a user with e-mail address or webhook URL.'
    )
    grp.add_argument(
        '-d', '--delete-user', metavar=('USER_ID'), nargs=1,
        help='delete a user.'
    )
    grp.add_argument(
        '-s', '--subscribe', metavar=('USER_ID', 'REPO:TAG'), nargs=2,
        help='subscribe to the Docker Hub repository.'
    )
    grp.add_argument(
        '-c', '--cancel', metavar=('USER_ID', 'REPO:TAG'), nargs=2,
        help='cancel to subscription of the Docker Hub repository.'
    )

    args = perser.parse_args()

    if args.list:
        show_list()
    elif args.register_user:
        register_user(*args.register_user)
    elif args.delete_user:
        delete_user(*args.delete_user)
    elif args.subscribe:
        subscribe_repository(*args.subscribe)
    elif args.cancel:
        unsubscribe_repository(*args.cancel)
    else:
        perser.print_help()
