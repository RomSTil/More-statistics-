import flet as ft
from flet import colors, icons
from db import Database

class ViewPage(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.db = Database()

        self.view_date_picker = ft.Dropdown(
            label="Выберите дату для просмотра",
            width=200,
            options=[],
            border_color=colors.BLUE_400,
            filled=True,
            border_radius=10,
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ФИО", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Баллы", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Дата", weight=ft.FontWeight.BOLD))
            ],
            rows=[],
            width=500,
            border=ft.border.all(1, colors.GREY_300),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, colors.GREY_300),
            horizontal_margin=20
        )

        self.controls = [
            ft.Text("Результаты студентов", size=1, weight=ft.FontWeight.BOLD),
            ft.Container(height=35),
            ft.Row(
                controls=[
                    self.view_date_picker,
                    ft.ElevatedButton(
                        "Обновить",
                        icon=icons.REFRESH,
                        on_click=lambda e: self.load_data(),
                        style=ft.ButtonStyle(
                            bgcolor=colors.BLUE_700,
                            color=colors.WHITE,
                            padding=15,
                            shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(height=15),
            ft.Container(
                content=self.data_table,
                padding=10,
            )
        ]
        self.scroll = ft.ScrollMode.AUTO

    def update_view_date_options(self):
        dates = self.db.get_dates()
        self.view_date_picker.options = [ft.dropdown.Option(date) for date in dates]
        if dates:
            self.view_date_picker.value = dates[0]
        if self.page:
            self.page.update()

    def load_data(self):
        if not self.view_date_picker.value:
            return

        data = self.db.get_data_by_date(self.view_date_picker.value)
        self.data_table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(row[1])),  # ФИО
                    ft.DataCell(ft.Text(str(row[2]))),  # Баллы
                    ft.DataCell(ft.Text(row[3]))  # Дата
                ]
            ) for row in data
        ]
        if self.page:  # Обновляем страницу, только если она существует
            self.page.update()