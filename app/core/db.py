import sqlite3

# SQLite 데이터베이스 설정
DB_NAME = "quiz.db"

def __init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idx INTEGER,
                topic_id INTEGER,
                quiz_type TEXT NOT NULL,
                question TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER,
                text TEXT,
                image_path TEXT,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            )
        ''')

__init_db()

def get_engine() -> sqlite3.Connection:
    return sqlite3.connect(DB_NAME)