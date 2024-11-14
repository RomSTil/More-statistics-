import sqlite3
import datetime

# Подключение к базе данных
conn = sqlite3.connect('leaderboard.db')
cursor = conn.cursor()

# Определение сегодняшней даты
current_date = datetime.date.today()

# Удаление записей за сегодняшний день
cursor.execute('DELETE FROM leader_data WHERE date = ?', (current_date,))

# Подтверждение изменений
conn.commit()

# Проверка, что данные удалены
deleted_rows = cursor.rowcount
if deleted_rows > 0:
    print(f"Данные за {current_date} успешно удалены.")
else:
    print(f"Записей за {current_date} не найдено.")

# Закрытие соединения
conn.close()
