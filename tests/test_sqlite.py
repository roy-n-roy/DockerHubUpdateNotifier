import sys
import os
import tempfile
import sqlite3

sys.path.append(os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir))
import entry_point

def test_create_table():
    temp_dir = tempfile.TemporaryDirectory()
    entry_point.DB_FILE = temp_dir.name + os.sep + "testdb.sqlite"

    if os.path.exists(entry_point.DB_FILE):
        os.remove(entry_point.DB_FILE)

    entry_point.db_create()

    with sqlite3.connect(entry_point.DB_FILE) as conn:
        # Tests for 'users' table
        (result,) = conn.execute('SELECT COUNT(*) FROM users').fetchone()
        assert isinstance(result, int)
        assert result == 0

        result = conn.execute('SELECT user_seq, user_id, mail_address, webhook_url FROM users').fetchone()
        assert result is None

        conn.execute('INSERT INTO users (user_id, mail_address, webhook_url) values (?, ?, ?)', ("test_user1", "test@mail.test", "http://url.test/"))
        result = conn.execute('SELECT user_seq, user_id, mail_address, webhook_url FROM users').fetchone()
        assert isinstance(result, tuple)
        assert len(result) == 4
        assert result == (1, "test_user1", "test@mail.test", "http://url.test/")

        # Tests for 'watching_repositories' table
        (result,) = conn.execute('SELECT COUNT(*) FROM watching_repositories').fetchone()
        assert isinstance(result, int)
        assert result == 0

        result = conn.execute('SELECT user_seq, publisher, repo_name, repo_tag, last_updated FROM watching_repositories').fetchone()
        assert result is None

        conn.execute('INSERT INTO watching_repositories (user_seq, repo_name, repo_tag) select user_seq, ?, ? from users where user_id = ?', ("nginx", "latest", "test_user1"))
        conn.execute('INSERT INTO watching_repositories (user_seq, publisher, repo_name, repo_tag) select user_seq, ?, ?, ? from users where user_id = ?', ("gitlab", "gitlab-ce", "latest", "test_user1"))
        result = conn.execute('SELECT user_seq, publisher, repo_name, repo_tag, last_updated FROM watching_repositories').fetchall()

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], tuple)
        assert isinstance(result[1], tuple)
        assert len(result[0]) == 5
        assert len(result[1]) == 5
        assert result[0] == (1, "library", "nginx", "latest", None)
        assert result[1] == (1, "gitlab", "gitlab-ce", "latest", None)
