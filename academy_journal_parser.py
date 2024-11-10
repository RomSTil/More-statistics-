from settings import password_journal, login_journal 
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import datetime
import json
import os

#Дата
current_date  = datetime.date.today()

#путь к папке
folder_path = 'jsons'

#имя файла и путь к файлу
file_name = f"leader_data_{current_date.strftime('%d')}_{current_date.strftime('%B')}_{current_date.strftime('%Y')}.json"
file_path = os.path.join(folder_path, file_name)

# массивы полнные имена и поинты
full_name_lst = []
points_lst = []


# Настройка драйвера
driver = webdriver.Chrome()  
driver.get("https://journal.top-academy.ru/ru/auth/login/index")

time.sleep(3)  

# Проверка на необходимость авторизации
try:
    # Ищем поле для ввода логина
    username = driver.find_element(By.NAME, "username")
    password = driver.find_element(By.NAME, "password")
    
    # Если поля найдены, выполняем авторизацию
    username.send_keys(login_journal)
    password.send_keys(password_journal)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    print("Авторизация выполнена успешно.")
    
    # Ждём загрузки страницы после авторизации
    time.sleep(3)
    
except:
    print("Авторизация не требуется или уже выполнена.")

# Переходим на страницу с рейтингом
driver.get("https://journal.top-academy.ru/ru/main/dashboard/page/index")
time.sleep(3)  



# BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Ищем все элементы 
leader_list = soup.find('ul', {'class': 'history-item leader'})

# Проверяем, удалось ли найти нужный список
if leader_list:

    leader_items = leader_list.find_all('li')
    

    for index, item in enumerate(leader_items, start=1):
        # Извлекаем текст 
        name_block = item.find('span', {'class': 'full-name-block'})
        name = name_block.get_text(strip=True) if name_block else "Имя не найдено"

        points_block = item.find('span', {'class': 'float-right point'})
        points = points_block.get_text(strip=True) if points_block else "Очки не найдены"
            
        full_name_lst.append(name)
        points_lst.append(points)
else:
    print("Не удалось найти элемент 'history-item leader'.")


data = {
    'full_name_lst': full_name_lst,
    'points_lst': points_lst
}

if not folder_path:
    os.makedirs(folder_path)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("данные сохранены")


# Закрываем драйвер
driver.quit()