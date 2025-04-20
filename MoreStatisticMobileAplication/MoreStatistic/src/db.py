import sqlite3
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name="leaderboard.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS leader_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                points INTEGER NOT NULL,
                date TEXT NOT NULL
            )
            """)
            conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
        finally:
            conn.close()

    def get_dates(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT date FROM leader_data ORDER BY date DESC")
            return [date[0] for date in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching dates: {e}")
            return []
        finally:
            conn.close()

    def get_data_by_date(self, date):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, full_name, points, date 
            FROM leader_data 
            WHERE date = ?
            ORDER BY points DESC
            """, (date,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return []
        finally:
            conn.close()

    def insert_data(self, data):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO leader_data (full_name, points, date) VALUES (?, ?, ?)",
                data
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            return False
        finally:
            conn.close()