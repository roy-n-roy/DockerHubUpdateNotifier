import gc
import os
import sys
import tempfile

from tzlocal import get_localzone

sys.path.append(os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir))
import edit_db
import entry_point


TEST_DB_FILE = 'testdb.sqlite'


def test_create_table():
    with tempfile.TemporaryDirectory() as tempdir:
        entry_point.DB_FILE = tempdir + os.sep + TEST_DB_FILE

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
            results = db['watching_repositories'].find(order_by=db['watching_repositories'].columns)

            assert results.next() == row1
            assert results.next() == row2

            results.close()
            db.close()
        del results
        del db
        gc.collect()

def test_add_user():
    with tempfile.TemporaryDirectory() as tempdir:
        entry_point.DB_FILE = tempdir + os.sep + TEST_DB_FILE

        if os.path.exists(entry_point.DB_FILE):
            os.remove(entry_point.DB_FILE)

        entry_point.db_create()

        edit_db.register_user('test_user1', 'test@gmail.com')
        edit_db.register_user('test_user2', 'http://hooks.slack.com/services/test')
        edit_db.register_user('test_user3', 'test@test.test')
        edit_db.register_user('test_user4', 'http://test.test/services/test')

        with entry_point.get_db() as db:
            assert db['users'].count() == 2
            assert db['users'].find_one(user_id='test_user1')['mail_address'] == 'test@gmail.com'
            assert db['users'].find_one(user_id='test_user1')['webhook_url'] == None
            assert db['users'].find_one(user_id='test_user2')['mail_address'] == None
            assert db['users'].find_one(user_id='test_user2')['webhook_url'] == 'http://hooks.slack.com/services/test'

            db.close()
        del db
        gc.collect()


def test_remove_user():
    with tempfile.TemporaryDirectory() as tempdir:
        entry_point.DB_FILE = tempdir + os.sep + TEST_DB_FILE

        if os.path.exists(entry_point.DB_FILE):
            os.remove(entry_point.DB_FILE)

        entry_point.db_create()

        edit_db.register_user('test_user1', 'test@gmail.com')
        edit_db.register_user('test_user2', 'http://hooks.slack.com/services/test')

        with entry_point.get_db() as db:
            assert db['users'].count() == 2

            edit_db.delete_user('test_user1')

            assert db['users'].count() == 1

            edit_db.delete_user('test_user3')

            assert db['users'].find_one(user_id='test_user1') is None
            assert db['users'].find_one(user_id='test_user2') is not None
            assert db['users'].find_one(user_id='test_user3') is None

            db.close()
        del db
        gc.collect()


def test_add_repo():
    with tempfile.TemporaryDirectory() as tempdir:
        entry_point.DB_FILE = tempdir + os.sep + TEST_DB_FILE

        if os.path.exists(entry_point.DB_FILE):
            os.remove(entry_point.DB_FILE)

        entry_point.db_create()

        edit_db.register_user('test_user1', 'test@gmail.com')

        with entry_point.get_db() as db:
            keys1 = dict(user_seq=1, publisher='library', repo_name='alpine', repo_tag='latest')
            check1 = dict(keys1.items())
            check1['last_updated'] = None
            edit_db.subscribe_repository('test_user1', 'alpine')
            assert db['watching_repositories'].count() == 1
            result1 = db['watching_repositories'].find_one(**keys1)
            assert result1['last_updated'] is not None
            result1['last_updated'] = None
            assert result1 == check1

            edit_db.subscribe_repository('test_user1', 'alpine') # duplicate.
            assert db['watching_repositories'].count() == 1

            edit_db.subscribe_repository('test_user1', 'alpine:latest') # duplicate.
            assert db['watching_repositories'].count() == 1
            result1 = db['watching_repositories'].find_one(**keys1)
            result1['last_updated'] = None
            assert result1 == check1


            edit_db.subscribe_repository('test_user1', 'alpine:3.10') # not duplicate.
            assert db['watching_repositories'].count() == 2
            keys2 = dict(keys1.items())
            keys2['repo_tag'] = '3.10'
            check2 = dict(keys2.items())
            check2['last_updated'] = None

            result1 = db['watching_repositories'].find_one(**keys1)
            result1['last_updated'] = None
            assert result1 == check1
            result2 = db['watching_repositories'].find_one(**keys2)
            result2['last_updated'] = None
            assert result2 == check2

            edit_db.subscribe_repository('test_user1', 'alpine:1') # not exists.
            assert db['watching_repositories'].count() == 2

            db.close()
        del db
        gc.collect()


def test_remove_repo():
    with tempfile.TemporaryDirectory() as tempdir:
        entry_point.DB_FILE = tempdir + os.sep + TEST_DB_FILE

        if os.path.exists(entry_point.DB_FILE):
            os.remove(entry_point.DB_FILE)

        entry_point.db_create()


        with entry_point.get_db() as db:

            db.close()
        del db
        gc.collect()
