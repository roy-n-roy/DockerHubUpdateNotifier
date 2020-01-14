import sys, os
import sqlite3

sys.path.append(os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir))
import entry_point

def test_create_table():
	entry_point.DB_FILE = "./testdb.sqlite"

	if os.path.exists(entry_point.DB_FILE):
		os.remove(entry_point.DB_FILE)

	entry_point.db_create()

	try:
		conn = sqlite3.connect(entry_point.DB_FILE)

		# Tests for 'users' table
		(result,) = conn.execute('SELECT COUNT(*) FROM users').fetchone()
		assert isinstance(result, int)
		assert result == 0

		result = conn.execute('SELECT user_id, mail_address, webhook_url FROM users').fetchone()
		assert result is None

		conn.execute('INSERT INTO users (mail_address, webhook_url) values ("test@mail.test", "http://url.test/")').fetchone()
		result = conn.execute('SELECT user_id, mail_address, webhook_url FROM users').fetchone()
		assert isinstance(result, tuple)
		assert len(result) == 3
		assert result == (1, "test@mail.test", "http://url.test/")

		# Tests for 'watching_repositories' table
		(result,) = conn.execute('SELECT COUNT(*) FROM watching_repositories').fetchone()
		assert isinstance(result, int)
		assert result == 0

		result = conn.execute('SELECT user_id, mail_address, webhook_url FROM watching_repositories').fetchone()
		assert result is None

		conn.execute('INSERT INTO watching_repositories (mail_address, webhook_url) values ("test@mail.test", "http://url.test/")').fetchone()
		result = conn.execute('SELECT user_id, mail_address, webhook_url FROM watching_repositories').fetchone()
		assert isinstance(result, tuple)
		assert len(result) == 3
		assert result == (1, "test@mail.test", "http://url.test/")

		conn.commit()
	finally:
		conn.close()

	if os.path.exists(entry_point.DB_FILE):
		os.remove(entry_point.DB_FILE)
