import sqlite3


class DB:
    def __init__(self):
        self.db_file = 'backend/users.db'

    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            chat_id TEXT UNIQUE
        )
        ''')
        conn.commit()
        conn.close()

    def add_user(self, chat_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO USERS (chat_id) VALUES (?)', (chat_id,))
        conn.commit()
        conn.close()

    def get_users(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM users')
        users = cursor.fetchall()
        conn.close()
        return [user[0] for user in users]


