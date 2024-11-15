import os
import time
import datetime
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
from settings import password_journal, login_journal

class LeaderboardScraper:
    def __init__(self, login, password, folder_path='jsons'):
        self.login = login
        self.password = password
        self.folder_path = folder_path
        self.driver = webdriver.Chrome()  # Настройка драйвера
        self.current_date = datetime.date.today()
        self.file_name = f"leader_data_{self.current_date.strftime('%d')}_{self.current_date.strftime('%B')}_{self.current_date.strftime('%Y')}.json"
        self.file_path = os.path.join(self.folder_path, self.file_name)
        self.full_name_lst = []
        self.points_lst = []

    def authenticate(self):
        """Метод для авторизации на сайте"""
        try:
            self.driver.get("https://journal.top-academy.ru/ru/auth/login/index")
            time.sleep(3)

            # Ищем поле для логина
            username = self.driver.find_element(By.NAME, "username")
            password = self.driver.find_element(By.NAME, "password")
            
            username.send_keys(self.login)
            password.send_keys(self.password)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            print("Авторизация выполнена успешно.")
            time.sleep(3)
        except NoSuchElementException as e:
            print(f"Ошибка при поиске элемента для авторизации: {e}")
        except TimeoutException as e:
            print(f"Превышено время ожидания: {e}")
        except Exception as e:
            print(f"Неизвестная ошибка при авторизации: {e}")

    def extract_data(self):
        """Метод для извлечения данных с страницы"""
        try:
            self.driver.get("https://journal.top-academy.ru/ru/main/dashboard/page/index")
            time.sleep(3)

            # Используем BeautifulSoup для парсинга страницы
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Ищем список лидеров
            leader_list = soup.find('ul', {'class': 'history-item leader'})

            if leader_list:
                leader_items = leader_list.find_all('li')

                for item in leader_items:
                    # Извлекаем имя
                    name_block = item.find('span', {'class': 'full-name-block'})
                    name = name_block.get_text(strip=True) if name_block else "Имя не найдено"

                    # Извлекаем поинты
                    points_block = item.find('span', {'class': 'float-right point'})
                    points = points_block.get_text(strip=True) if points_block else "Очки не найдены"
                    
                    self.full_name_lst.append(name)
                    self.points_lst.append(points)
                print("Данные успешно извлечены.")
            else:
                print("Не удалось найти элемент 'history-item leader'.")
        except Exception as e:
            print(f"Ошибка при извлечении данных: {e}")

    def save_to_json(self):
        """Метод для сохранения данных в JSON файл"""
        try:
            data = {
                'full_name_lst': self.full_name_lst,
                'points_lst': self.points_lst
            }

            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)

            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print("Данные сохранены.")
        except Exception as e:
            print(f"Ошибка при сохранении данных в файл: {e}")

    def close_driver(self):
        """Метод для закрытия драйвера"""
        self.driver.quit()
        print("Драйвер закрыт.")

# Пример использования класса
if __name__ == '__main__':
    scraper = LeaderboardScraper(login_journal, password_journal)

    # Пошаговое выполнение
    scraper.authenticate()
    scraper.extract_data()
    scraper.save_to_json()
    scraper.close_driver()
