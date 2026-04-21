import time
import re

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

#-------------------------------------------ОБЯЗАТЕЛЬНО ДЛЯ ВВОДА-------------------------------------------#

start = datetime.strptime("04.05.2025", "%d.%m.%Y") # Дата старта, с которой открываем монитор
end   = datetime.strptime("11.12.2025", "%d.%m.%Y") # Дата окончания
login_aa = "salikov_z" #сменить логин и пароль на свой от УЗ
password_aa = "1111"

start_url = "https://fms.smartagro.ru" #стартовая страница. Если на проде, не меняем

#-------------------------------------------ОБЯЗАТЕЛЬНО ДЛЯ ВВОДА-------------------------------------------#

def wait_apex(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "u-Processing"))
    )
def active_md(driver): #функция активации МД
    driver.find_element("id", "B315650059629473018").click() #Активировать
    wait_apex(driver)
    time.sleep(3)
    wait_apex(driver)
    driver.find_element("id", "B1353084897237056520").click() #Добавление техники
    wait_apex(driver)
    time.sleep(1)
    iframe = driver.find_element(By.CSS_SELECTOR, 'iframe[title="Добавление техники в монитор"]') #Ищем в новом фрейме
    driver.switch_to.frame(iframe)

    # Теперь ищем кнопку внутри iframe
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "P664_ECHID_MOVE_ALL")) #Добавить всю технику
    )
    button.click()

    time.sleep(0.5)
    driver.find_element("id", "B456189928152782371").click() #Применить
    driver.switch_to.default_content()

#логинимся
driver.get(start_url)
wait_apex(driver)
driver.find_element("id", "P101_USERNAME").send_keys(login_aa)
driver.find_element("id", "P101_PASSWORD").send_keys(password_aa)
driver.find_element("id", "b-login").click()
wait_apex(driver)

current_url = driver.current_url
new_url = re.sub(r"(f\?p=\d+):\d+:(\d+)", r"\1:458:\2", current_url) #меняем номер страницы сохраняя сессию и прочее в current_url
driver.get(new_url)
wait_apex(driver)


current = start
while current <= end:
    date_str = current.strftime("%d.%m.%Y")
    time.sleep(3)
    wait_apex(driver)
    date_input = driver.find_element("id", "P458_DATE") #Меняем дату в фильтре мд
    date_input.clear()
    date_input.send_keys(date_str)
    date_input.send_keys(Keys.TAB)
    active_md(driver)
#-------------------------------------------ВАЖНО-------------------------------------------#

#       Если какие-то даты активированы,
#       убрать комментарий с куска кода ниже ↓↓↓

#       По желанию, можно увеличить время в строке WebDriverWait(driver, 10).
#       Конкретно вместо 10 поставить 15 секунд.
#       Но в таком случае, если мд не активирован, интерпретатор будет 15 секунд ждать,
#       пока не убедится в том, что таблица в МД не прогрузилась.
#       Только тогда он его активирует и добавит технику. Иначе просто перейдет на последующую дату

# -----------------------------------------↓↓↓----------------------------------------------#

    # try: #Проверяем активирован ли МД наличием столбца в таблице. Может подлагивать
    #     wait_apex(driver)
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.CLASS_NAME, 'a-IRR-header'))
    #     )
    #     print("Монитор активирован")
    #     pass
    # except TimeoutException: #Переключаемся на следующую дату
    #     print("Монитор не активирован")
    #     active_md(driver)

# -----------------------------------------↑↑↑------------------------------------------

    # шаг +1 день
    current += timedelta(days=1)




