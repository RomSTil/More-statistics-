import sqlite3
import datetime
import flet as ft

# Функция для получения данных из базы данных по дате
def get_data_by_date(date):
    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, points FROM leader_data WHERE date = ?", (date,))
    results = cursor.fetchall()
    conn.close()
    return results

# Основная функция приложения Flet
def main(page: ft.Page):
    page.title = "Просмотр данных по дате"
    page.horizontal_alignment = "center"  
    page.vertical_alignment = "center"    

    # Поле для ввода даты
    date_input = ft.TextField(
        label="Введите дату (ГГГГ-ММ-ДД):",
        hint_text="Например, 2024-11-09",
        width=200,
        text_align="center"
        
        
    )

    # Прокручиваемый список для строк таблицы
    data_list = ft.ListView(
        height=300,   # Ограничиваем высоту, чтобы активировать прокрутку
        width=400,
        spacing=10,
        padding=10,
        auto_scroll=False,
    )

    # Функция загрузки данных
    def load_data(e):
        # Проверка формата даты
        try:
            selected_date = datetime.datetime.strptime(date_input.value, "%Y-%m-%d").date()
            data = get_data_by_date(selected_date.strftime("%Y-%m-%d"))
            
            if data:
                # Очистка списка перед загрузкой новых данных
                data_list.controls.clear()
                
                # Добавление строк данных в ListView
                for full_name, points in data:
                    row = ft.Row(
                        controls=[
                            ft.Text(full_name, width=200),
                            ft.Text(str(points), width=100),
                        ],
                        alignment="spaceBetween",
                    )
                    data_list.controls.append(row)
                page.snack_bar = ft.SnackBar(ft.Text(f"Данные за {selected_date} успешно загружены."))
                page.snack_bar.open = True
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Данные за {selected_date} отсутствуют."))
                page.snack_bar.open = True
                page.update()
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Ошибка: Неверный формат даты. Используйте ГГГГ-ММ-ДД."))
            page.snack_bar.open = True
            page.update()

    # Кнопка для загрузки данных
    load_button = ft.ElevatedButton("Загрузить данные", on_click=load_data)

    # Добавление элементов на страницу и выравнивание по центру
    page.add(
        ft.Column(
            controls=[
                date_input,
                load_button,
                data_list  # Добавляем ListView на страницу
            ],
            alignment="center",
            horizontal_alignment="center",
        )
    )

# Запуск приложения
ft.app(target=main)
