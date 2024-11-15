""" LoadData """

import json
import sqlite3
import datetime
import logging
logging.basicConfig(level=logging.INFO)  # Инициализация базового логгера

class LoadData:
    def __init__(self, conn, cursor, current_date, file_name, file_path, data, names, points):
        self.conn = conn
        self.cursor = cursor
        self.current_date = current_date
        self.file_name = file_name
        self.file_path = file_path
        self.data = data
        self.names = names
        self.points = points

    def setup_leader_data_table(self):
        """ проверка на существования бд в случаее отсутствия """
        try:
            self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS leader_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            points INTEGER NOT NULL,
            date TEXT NOT NULL
            )
            ''')
            logging.info("Таблица leader_data успешно создана или уже существует.")
        except Exception as e:
            logging.error(f"Ошибка при создании таблицы: {e}")

    def load_in_db(self):
        """ Загрузка данных в бд через json файл"""
        self.cursor.execute("SELECT 1 FROM leader_data WHERE date = ?", (self.current_date,))
        if self.cursor.fetchone():
            print(f"Файл за {self.current_date} уже был загружен ранее. Повторная загрузка отменена.")
        else:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                logging.error(f"Ошибка при чтении файла {e}")
                return
            
            self.names = self.data.get("full_name_lst", [])
            self.points = self.data.get("points_lst", [])
            
            if len(self.names) == len(self.points):
                for name, point in zip(self.names, self.points):
                    self.cursor.execute(''' 
                    INSERT INTO leader_data (full_name, points, date)
                    VALUES (?, ?, ?)
                    ''', (name, int(point), self.current_date))
                print(f"Данные за {self.current_date} успешно загружены в базу данных.")
            else:
                print("Ошибка: списки 'full_name_lst' и 'points_lst' имеют разную длину.")

    def main(self):
        self.setup_leader_data_table()
        self.load_in_db()
        self.conn.commit()  # Не забудьте закоммитить изменения в базу данных
        self.conn.close()

conn = sqlite3.connect('leaderboard.db')
cursor = conn.cursor()

current_date  = datetime.date.today()
file_name = f"leader_data_{current_date.strftime('%d')}_{current_date.strftime('%B')}_{current_date.strftime('%Y')}.json"
file_path = f"jsons/{file_name}"

# Теперь создание объекта LoadData
obj = LoadData(conn, cursor, current_date, file_name, file_path, None, None, None)


if "__main__" == __name__:
    obj.main()
