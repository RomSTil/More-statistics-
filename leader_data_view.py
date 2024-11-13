import sqlite3
import datetime
import pandas as pd
import flet as ft

# Функция для получения данных из базы данных по дате
def get_data_by_date(date):
    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, points FROM leader_data WHERE date = ?", (date,))
    results = cursor.fetchall()
    conn.close()
    return results

# Функция для расчета прироста поинтов по участнику
def get_points_growth_by_name(name, specific_date):
    # Подключаемся к базе данных
    conn = sqlite3.connect("leaderboard.db")
    query = "SELECT full_name, points, date FROM leader_data WHERE full_name = ? ORDER BY date;"
    data = pd.read_sql_query(query, conn, params=(name,))
    conn.close()

    # Преобразуем дату в формат datetime и сортируем по дате
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values(by=['date'])

    # Рассчитываем прирост поинтов для участника между датами
    data['points_diff'] = data['points'].diff().fillna(0).astype(int)
    
    # Фильтруем прирост только для указанной даты
    specific_date = pd.to_datetime(specific_date)
    data = data[data['date'] == specific_date]

    # Формируем результат в виде списка строк для отображения
    growth_info = []
    for _, row in data.iterrows():
        points_info = f"{row['date'].date()} - {row['points']} поинтов"
        
        # Указываем прирост или уменьшение поинтов
        if row['points_diff'] > 0:
            points_info += f" - +{row['points_diff']} прибавок"
        elif row['points_diff'] < 0:
            points_info += f" - {row['points_diff']} (уменьшение)"
        else:
            points_info += " - +0 прибавок"
        
        growth_info.append(points_info)
    return growth_info

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
        height=300,
        width=400,
        spacing=10,
        padding=10,
        auto_scroll=False,
    )

    # Прокручиваемый список для отображения прироста поинтов ученика
    growth_list = ft.ListView(
        height=200,
        width=400,
        spacing=10,
        padding=10,
        auto_scroll=False,
    )

   # Функция для обновления отображаемого прироста поинтов с иконками
    def show_growth_by_name(full_name):
        growth_data = get_points_growth_by_name(full_name, date_input.value)  # Передаем выбранную дату
        growth_list.controls.clear()

        if growth_data:
            for line in growth_data:
                # Для улучшения восприятия, каждую строку можно стилизовать
                text_style = ft.TextStyle(size=16, weight="bold")
                
                # Проверяем прирост или уменьшение
                if "прибавок" in line:
                    # Строка с прибавками, добавляем иконку стрелки вверх
                    growth_list.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.ARROW_CIRCLE_UP, color=ft.colors.GREEN),  # Иконка стрелки вверх
                                ft.Text(line, style=text_style, color=ft.colors.GREEN),
                            ],
                            alignment="start",  # Выравнивание по левому краю
                            vertical_alignment="center"
                        )
                    )
                elif "уменьшение" in line:
                    # Строка с уменьшением, добавляем иконку стрелки вниз
                    growth_list.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.ARROW_CIRCLE_DOWN, color=ft.colors.RED),  # Иконка стрелки вниз
                                ft.Text(line, style=text_style, color=ft.colors.RED),
                            ],
                            alignment="start",  # Выравнивание по левому краю
                        )
                    )
                else:
                    # Стандартная строка без изменений, просто текст
                    growth_list.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.INFO, color=ft.colors.BLACK),  # Иконка информации
                                ft.Text(line, style=text_style, color=ft.colors.BLACK),
                            ],
                            alignment="start",  # Выравнивание по левому краю
                        )
                    )

            page.snack_bar = ft.SnackBar(ft.Text(f"История прироста поинтов для {full_name} за {date_input.value} загружена."))
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"Данные для {full_name} за {date_input.value} отсутствуют."))
        
        page.snack_bar.open = True
        page.update()
        
    # Функция загрузки данных по дате
    def load_data(e):
        try:
            selected_date = datetime.datetime.strptime(date_input.value, "%Y-%m-%d").date()
            data = get_data_by_date(selected_date.strftime("%Y-%m-%d"))
            
            if data:
                data_list.controls.clear()
                for full_name, points in data:
                    row = ft.Row(
                        controls=[
                            ft.TextButton(
                                text=full_name, 
                                width=200,
                                on_click=lambda e, name=full_name: show_growth_by_name(name)
                            ),
                            ft.Text(str(points), width=100),
                        ],
                        alignment="spaceBetween",
                    )
                    data_list.controls.append(row)
                
                page.snack_bar = ft.SnackBar(ft.Text(f"Данные за {selected_date} успешно загружены."))
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

    # Компоновка элементов на странице
    page.add(
        ft.Column(
            controls=[
                date_input,
                load_button,
                ft.Row(
                    controls=[data_list, growth_list],  
                    alignment="center"
                ),
            ],
            alignment="center",
            horizontal_alignment="center",
        )
    )

# Запуск приложения
ft.app(target=main)
