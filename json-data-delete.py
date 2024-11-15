import sqlite3
import datetime

class DeleteDate:
    def __init__(self, conn, cursor, current_date):
        self.conn = conn
        self.cursor = cursor
        self.current_date = current_date

    def delete_in_db(self):
        """ Удаление информации за сегодняшнюю дату """
        try:
            self.cursor.execute('DELETE FROM leader_data WHERE date = ?', (self.current_date,))
            self.conn.commit()
            deleted_rows = self.cursor.rowcount
            
            if deleted_rows > 0:
                return f"удалены все данные за {self.current_date}"
            else:
                return f"Записей за {self.current_date} нет"
        except sqlite3.DatabaseError as e:
            return f"ошибка базы данных: {e}"
        
    def __del__(self):
        if self.conn:
            self.conn.close()


# Подключеение
conn = sqlite3.connect('leaderboard.db')
cursor = conn.cursor()

current_date = datetime.date.today()

obj = DeleteDate(conn, cursor, current_date)
print(obj.delete_in_db())