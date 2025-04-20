import flet as ft
from pages.import_page import ImportPage
from pages.view_page import ViewPage

def main(page: ft.Page):
    # Настройки страницы
    page.title = "Student Points Manager"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1080
    page.window_height = 1920
    page.padding = 0
    page.spacing = 10
    page.vertical_alignment = ft.MainAxisAlignment.SPACE_BETWEEN
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Инициализация страниц
    import_page = ImportPage(page)
    view_page = ViewPage(page)

    # Навигация
    def change_tab(e):
        index = e.control.selected_index
        content.content = [import_page, view_page][index]
        if index == 1:
            view_page.update_view_date_options()
            view_page.load_data()
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.icons.UPLOAD,
                selected_icon=ft.icons.CLOUD_UPLOAD,
                label="Импорт"
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.TABLE_VIEW,
                label="Просмотр"
            ),
        ],
        on_change=change_tab,
        selected_index=0,
        height=110,
        elevation=0,
        bgcolor=ft.colors.SURFACE_VARIANT
    )

    # Основной layout
    content = ft.Container(content=import_page, expand=True)

    page.add(
        ft.Column(
            controls=[
                ft.Container(
                    content=content,
                    expand=True,
                    alignment=ft.alignment.center
                ),
                nav_bar
            ],
            expand=True,
            spacing=0
        )
    )

if __name__ == "__main__":
    ft.app(target=main)