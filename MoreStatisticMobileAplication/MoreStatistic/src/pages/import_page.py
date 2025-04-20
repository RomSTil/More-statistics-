import datetime
import requests
import flet as ft
from flet import colors, icons
from db import Database

class ImportPage(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.db = Database()
        
        self.url_input = ft.TextField(
            label="URL JSON-файла",
            width=600,
            hint_text="https://example.com/data.json",
            border_color=colors.BLUE_400,
            filled=True,
            border_radius=10,
            prefix_icon=icons.LINK
        )

        self.date_picker = ft.TextField(
            label="Дата данных (ДД-Месяц-ГГГГ)",
            width=300,
            value=datetime.date.today().strftime('%d-%B-%Y'),
            border_color=colors.BLUE_400,
            filled=True,
            border_radius=10,
            prefix_icon=icons.DATE_RANGE
        )

        self.status_display = ft.Text("", color=colors.GREY_600)
        self.progress_ring = ft.ProgressRing(width=20, height=20, visible=False)

        self.import_button = ft.ElevatedButton(
            "Загрузить данные",
            icon=icons.CLOUD_UPLOAD,
            on_click=self.import_data,
            style=ft.ButtonStyle(
                bgcolor=colors.BLUE_700,
                color=colors.WHITE,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            width=300
        )

        self.controls = [
            ft.Text("Импорт данных", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            self.url_input,
            ft.Container(height=10),
            self.date_picker,
            ft.Container(height=20),
            ft.Row([self.import_button, self.progress_ring], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            self.status_display
        ]
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def import_data(self, e):
        self.import_button.disabled = True
        self.progress_ring.visible = True
        self.status_display.value = "⏳ Идет загрузка данных..."
        self.page.update()

        url = self.url_input.value.strip()
        if not url:
            self.status_display.value = "❌ Введите URL!"
            self.import_button.disabled = False
            self.progress_ring.visible = False
            self.page.update()
            return

        try:
            date_str = self.date_picker.value.strip()
            datetime.datetime.strptime(date_str, '%d-%B-%Y').date()  # Проверка формата
        except ValueError:
            self.status_display.value = "❌ Неверный формат даты! Используйте ДД-Месяц-ГГГГ"
            self.import_button.disabled = False
            self.progress_ring.visible = False
            self.page.update()
            return

        # Проверка на существование данных
        if date_str in self.db.get_dates():
            self.status_display.value = f"❌ Данные за {date_str} уже существуют!"
            self.import_button.disabled = False
            self.progress_ring.visible = False
            self.page.update()
            return

        # Загрузка JSON
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()

            if "full_name_lst" in json_data and "points_lst" in json_data:
                names = json_data["full_name_lst"]
                points = json_data["points_lst"]

                if len(names) != len(points):
                    self.status_display.value = "❌ Количество имен и баллов не совпадает!"
                    self.import_button.disabled = False
                    self.progress_ring.visible = False
                    self.page.update()
                    return

                clean_names = [name.split('.', 1)[-1].strip() if '.' in name else name.strip() for name in names]
                data_to_insert = [(name, int(point), date_str) for name, point in zip(clean_names, points)]

                if self.db.insert_data(data_to_insert):
                    self.status_display.value = f"✅ Импортировано {len(clean_names)} записей за {date_str}"
                else:
                    self.status_display.value = "❌ Ошибка при сохранении в базу данных"
            else:
                self.status_display.value = "❌ Неверный формат JSON: отсутствуют full_name_lst или points_lst"
        except requests.RequestException as re:
            self.status_display.value = f"❌ Ошибка сети: {str(re)}"
        except Exception as e:
            self.status_display.value = f"❌ Ошибка: {str(e)}"
        finally:
            self.import_button.disabled = False
            self.progress_ring.visible = False
            self.page.update()