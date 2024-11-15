#                        
#　　　　　　　　　　_,.. -──- ､,
#　　　　　　　　,　'" 　 　　　 　　 `ヽ.
#　　　　　　 ／/¨7__　　/ 　 　 i　 _厂廴
#　　　　　 /￣( ノ__/　/{　　　　} ｢　（_冫}
#　　　　／￣l＿// 　/-|　 ,!　 ﾑ ￣|＿｢ ＼＿_
#　　. イ　 　 ,　 /!_∠_　|　/　/_⊥_,ﾉ ハ　 イ 
#　　　/ ／ / 　〃ん心 ﾚ'|／　ｆ,心 Y　i ＼_＿＞　
#　 ∠イ 　/　 　ﾄ弋_ツ　　 　 弋_ﾂ i　 |　 | ＼
#　 _／ _ノ|　,i　⊂⊃　　　'　　　⊂⊃ ./　 !､＿ン
#　　￣　　∨|　,小、　　` ‐ ' 　　 /|／|　/
#　 　 　 　 　 Y　|ﾍ＞ 、 ＿ ,.　イﾚ|　 ﾚ'
#　　　　　　 r'.| 　|;;;入ﾞ亠―亠' );;;;;! 　|､
#　　　　　 ,ノ:,:|.　!|く　__￣￣￣__У　ﾉ|:,:,ヽ
#　　　　　(:.:.:.:ﾑ人!ﾍ　 　` ´ 　　 厂|ノ:.:.:丿 by @RomSTil
""" View Data """
import sqlite3
import datetime
import pandas as pd
import flet as ft

class LeaderboardApp:
    def __init__(self):
        self.date_input = None
        self.data_list = None
        self.growth_list = None

    # Функция для получения данных из базы данных по дате
    def get_data_by_date(self, date):
        conn = sqlite3.connect("leaderboard.db")
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, points FROM leader_data WHERE date = ?", (date,))
        results = cursor.fetchall()
        conn.close()
        return results

    # Функция для расчета прироста поинтов по участнику
    def get_points_growth_by_name(self, name, specific_date):
        conn = sqlite3.connect("leaderboard.db")
        query = "SELECT full_name, points, date FROM leader_data WHERE full_name = ? ORDER BY date;"
        data = pd.read_sql_query(query, conn, params=(name,))
        conn.close()

        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values(by=['date'])

        data['points_diff'] = data['points'].diff().fillna(0).astype(int)
        specific_date = pd.to_datetime(specific_date)
        data = data[data['date'] == specific_date]

        growth_info = []
        for _, row in data.iterrows():
            points_info = f"{row['date'].date()} - {row['points']} поинтов"
            if row['points_diff'] > 0:
                points_info += f" - +{row['points_diff']} прибавок"
            elif row['points_diff'] < 0:
                points_info += f" - {row['points_diff']} (уменьшение)"
            else:
                points_info += " - +0 прибавок"
            growth_info.append(points_info)
        return growth_info

    # Загрузка данных о таблице лидеров
    def load_data(self, page, e):
        if not self.date_input.value:
            self.show_snackbar(page, "Ошибка: Пожалуйста, введите дату.")
            return

        try:
            selected_date = datetime.datetime.strptime(self.date_input.value, "%Y-%m-%d").date()
            data = self.get_data_by_date(selected_date.strftime("%Y-%m-%d"))
            
            if data:
                self.data_list.controls.clear()
                for full_name, points in data:
                    row = ft.Row(
                        controls=[
                            ft.TextButton(
                                text=full_name,
                                width=200,
                                on_click=lambda e, name=full_name: self.show_growth_by_name(page, name)
                            ),
                            ft.Text(str(points), width=100),
                        ],
                        alignment="spaceBetween",
                    )
                    self.data_list.controls.append(row)
                self.show_snackbar(page, f"Данные за {selected_date} успешно загружены.")
            else:
                self.show_snackbar(page, f"Данные за {selected_date} отсутствуют.")
            
            page.update()
        except ValueError:
            self.show_snackbar(page, "Ошибка: Неверный формат даты. Используйте ГГГГ-ММ-ДД.")

    # Отображение прироста поинтов
    def show_growth_by_name(self, page, full_name):
        growth_data = self.get_points_growth_by_name(full_name, self.date_input.value)
        self.growth_list.controls.clear()

        if growth_data:
            for line in growth_data:
                text_style = ft.TextStyle(size=16, weight="bold")
                if "прибавок" in line:
                    self.growth_list.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.ARROW_CIRCLE_UP, color=ft.colors.GREEN),
                                ft.Text(line, style=text_style, color=ft.colors.GREEN),
                            ],
                            alignment="start",
                        )
                    )
                elif "уменьшение" in line:
                    self.growth_list.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.ARROW_CIRCLE_DOWN, color=ft.colors.RED),
                                ft.Text(line, style=text_style, color=ft.colors.RED),
                            ],
                            alignment="start",
                        )
                    )
                else:
                    self.growth_list.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.INFO, color=ft.colors.BLACK),
                                ft.Text(line, style=text_style, color=ft.colors.BLACK),
                            ],
                            alignment="start",
                        )
                    )
            self.show_snackbar(page, f"История прироста поинтов для {full_name} за {self.date_input.value} загружена.")
        else:
            self.show_snackbar(page, f"Данные для {full_name} за {self.date_input.value} отсутствуют.")

        page.update()

    # Показать уведомление
    def show_snackbar(self, page, message):
        page.snack_bar = ft.SnackBar(ft.Text(message))
        page.snack_bar.open = True

    # Основная функция приложения
    def main(self, page: ft.Page):
        page.title = "Просмотр данных по дате"
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"

        self.date_input = ft.TextField(
            label="Введите дату (ГГГГ-ММ-ДД):",
            hint_text="Например, 2024-11-09",
            width=200,
            text_align="center"
        )
        load_button = ft.ElevatedButton("Загрузить данные", on_click=lambda e: self.load_data(page, e))
        self.data_list = ft.ListView(height=300, width=400, spacing=10, padding=10, auto_scroll=False)
        self.growth_list = ft.ListView(height=200, width=400, spacing=10, padding=10, auto_scroll=False)

        content_area = ft.Column(
            controls=[
                self.date_input,
                load_button,
                ft.Row(controls=[self.data_list, self.growth_list], alignment="center"),
            ],
            horizontal_alignment="center",
        )
        page.add(content_area)

# Запуск приложения
ft.app(target=LeaderboardApp().main)

