import json
import sqlite3
import datetime

conn = sqlite3.connect('leaderboard.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS leader_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    points INTEGER NOT NULL,
    date TEXT NOT NULL
)
''')    

current_date  = datetime.date.today()
file_name = f"leader_data_{current_date.strftime('%d')}_{current_date.strftime('%B')}_{current_date.strftime('%Y')}.json"
file_path = f"jsons/{file_name}"

cursor.execute('SELECT 1 FROM leader_data WHERE date = ?', (current_date,))
if cursor.fetchone():
    print(f"Файл за {current_date} уже был загружен ранее. Повторная загрузка отменена.")
else:
    # Загрузка данных из JSON-файла
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)


    names = data.get("full_name_lst", [])
    points = data.get("points_lst", [])

    if len(names) == len(points):
        for name, point in zip(names, points):
            cursor.execute('''
            INSERT INTO leader_data (full_name, points, date)
            VALUES (?, ?, ?)
            ''', (name, int(point), current_date))
        print(f"Данные за {current_date} успешно загружены в базу данных.")
    else:
        print("Ошибка: списки 'full_name_lst' и 'points_lst' имеют разную длину.")

    conn.commit()
    conn.close()

    print("Данные успешно сохранены")

