import gc
import os
import sys
import tempfile

from tzlocal import get_localzone

sys.path.append(os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir))
import edit
import entry_point


def test_create_table():
    with tempfile.TemporaryDirectory() as tempdir:
        entry_point.DB_FILE = tempdir + os.sep + "testdb.sqlite"

        if os.path.exists(entry_point.DB_FILE):
            os.remove(entry_point.DB_FILE)

        entry_point.db_create()

        with entry_point.get_db() as db:
            # Tests for 'users' table
            assert db['users'].count() == 0

            row = dict(user_id="test_user1", mail_address="test@mail.test", webhook_url="http://url.test/", timezone=get_localzone().zone)
            db['users'].insert(row)
            row['user_seq'] = 1
            assert  db['users'].find_one() == row

            # Tests for 'watching_repositories' table
            assert db['watching_repositories'].count() == 0

            row1 = dict(user_seq=1, publisher="gitlab", repo_name="gitlab-ce", repo_tag="latest")
            row2 = dict(user_seq=1, repo_name="nginx", repo_tag="latest")
            db['watching_repositories'].insert(row1)
            db['watching_repositories'].insert(row2)

            row1['last_updated'] = None
            row2['publisher'] = 'library'
            row2['last_updated'] = None
            data = db['watching_repositories'].find(order_by=db['watching_repositories'].columns)

            assert data.next() == row1
            assert data.next() == row2

            data.close()
            db.close()
        del data
        del db
        gc.collect()

def test_add_user():
    with tempfile.TemporaryDirectory() as tempdir:
        entry_point.DB_FILE = tempdir + os.sep + "testdb.sqlite"

        if os.path.exists(entry_point.DB_FILE):
            os.remove(entry_point.DB_FILE)

        entry_point.db_create()

        edit.register_user('test_user1', 'test@gmail.com')
        edit.register_user('test_user2', 'http://hooks.slack.com/services/test')
        edit.register_user('test_user3', 'test@test.test')
        edit.register_user('test_user4', 'http://test.test/services/test')

        with entry_point.get_db() as db:
            assert db['users'].count() == 2
            assert db['users'].find_one(user_id='test_user1')['mail_address'] == 'test@gmail.com'
            assert db['users'].find_one(user_id='test_user1')['webhook_url'] == None
            assert db['users'].find_one(user_id='test_user2')['mail_address'] == None
            assert db['users'].find_one(user_id='test_user2')['webhook_url'] == 'http://hooks.slack.com/services/test'

            db.close()
        del db
        gc.collect()
