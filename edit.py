import argparse
from entry_point import get_db, VERSION
import logging
import os
from urllib3.util import parse_url

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
    argperser = argparse.ArgumentParser(description="Docker Hub Update Notifier.", add_help=False)
    arggroup = argperser.add_mutually_exclusive_group()
    arggroup.add_argument('-h', '--help', action='help')
    arggroup.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
    arggroup.add_argument('-l', '--list', help='show list of users and subscriptions.', action='store_true')
    arggroup.add_argument('-r', '--register-user', help='registering a user with e-mail address or webhook URL.', metavar=('USER_ID', 'EMAIL_or_WEBHOOK'), nargs=2)
    arggroup.add_argument('-d', '--delete-user', help='delete a user.', metavar=('USER_ID'), nargs=1)
    arggroup.add_argument('-s', '--subscribe', help='subscribe to the Docker Hub repository.', metavar=('USER_ID','REPO:TAG'), nargs=2)
    arggroup.add_argument('-c', '--cancel', help='cancel to subscription of the Docker Hub repository.', metavar=('USER_ID','REPO:TAG'), nargs=2)

    args = argperser.parse_args()

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
        argperser.print_help()
