import json
import re
import time
from fields import fields_dict
from urllib.parse import urlparse
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, UnexpectedTagNameException
import pandas

base_url = 'https://fms.smartagro.ru'
############################
# Базовые функции Selenium
############################
def create_browser(headless=False, implicit_wait=5):
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.implicitly_wait(implicit_wait)
    return driver


def wait_for_ready(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


############################
# Авторизация и работа с сессией
############################
def login_apex(driver, login_url, username, password):
    """
    Авторизация в Oracle APEX.
    Возвращает session_id (число в параметре f?p=...:SESSION_ID:...).
    """
    driver.get(login_url)
    wait_for_ready(driver)

    # Пытаемся найти стандартные поля Oracle APEX
    user_input = driver.find_element(By.ID, "P101_USERNAME")
    pass_input = driver.find_element(By.ID, "P101_PASSWORD")
    submit_btn = driver.find_element(By.ID, "b-login")

    user_input.clear()
    user_input.send_keys(username)
    pass_input.clear()
    pass_input.send_keys(password)
    time.sleep(2)
    submit_btn.click()
    wait_for_ready(driver)
    time.sleep(2)

    # Извлекаем session_id из текущего URL
    session_id = extract_apex_session(driver.current_url)
    if not session_id:
        raise RuntimeError("Не удалось определить session_id после логина")

    print(f"[INFO] Авторизация успешна, session_id = {session_id}")
    return session_id


def extract_apex_session(url: str) -> str | None:
    """Извлекает SESSION_ID из APEX URL"""
    match = re.search(r"f\?p=\d+:\d+:(\d+):", url)
    return match.group(1) if match else None


def build_apex_url(app_id: int, page_id: int, session_id: str, params: str = "") -> str:
    """Формирует корректный APEX URL с заданной сессией"""
    base = f"{base_url}/ords/"
    url = f"{base}f?p={app_id}:{page_id}:{session_id}::{params}"
    return url


############################
# Вспомогательные функции
############################
def find_element(driver, by, value, timeout=10):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    return driver.find_element(by, value)


def find_and_click(driver, by, value, timeout=10):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
    el.click()
    return el


def wait_for_element(driver, by, value, timeout=10):
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
    return 1

def find_and_input(driver, by, search, value, timeout=10):
    click = driver.find_element(by, search)
    click.clear()
    click.send_keys(value)
    click.send_keys(Keys.ENTER)
    return click

def to_frame(driver):#Перключение на модальное окно
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    driver.switch_to.frame(iframe)

def back_frame(driver):#Вернуться к главной странице
    driver.switch_to.default_content()


def select_elem(driver, by, search, text, log=True):
    """
    Выбирает элемент из <select> по частичному совпадению текста.

    :param driver: Selenium WebDriver
    :param locator_type: Тип локатора (By.ID, By.NAME, By.XPATH и т.д.)
    :param locator_value: Значение локатора
    :param partial_text: Подстрока, которую нужно найти в <option>.text
    :param log: Включить логирование
    :return: True, если успешно выбрано; False, если не найдено
    """
    try:
        element = driver.find_element(by, search)
        select = Select(element)

        # Поиск опции по частичному совпадению текста
        matched_option = None
        for opt in select.options:
            if text.lower() in opt.text.strip().lower():
                matched_option = opt
                break

        if not matched_option:
            if log:
                print(f"[!] Не найдено ни одной опции, содержащей '{text}'")
            return False

        # Проверка, уже выбрана ли эта опция
        if matched_option.is_selected():
            if log:
                print(f"[✓] Опция '{matched_option.text}' уже выбрана.")
            return True

        # Выбор опции
        select.select_by_visible_text(matched_option.text)
        if log:
            print(f"[→] Выбрана опция: '{matched_option.text}'")
        return True

    except NoSuchElementException:
        if log:
            print(f"[!] Элемент <select> не найден: {by}='{search}'")
        return False
    except UnexpectedTagNameException:
        if log:
            print(f"[!] Элемент не является <select>: {by}='{search}'")
        return False



############################
# Пример использования
############################
if __name__ == "__main__":
    LOGIN_URL = f"{base_url}/ords/f?p=901:LOGIN::::::"
    USERNAME = "salikov_z"
    PASSWORD = "1111"

    # Пример: после логина перейти на страницу 700 приложения 802
    APP_ID = 802
    PAGE_ID = 700

    driver = create_browser(headless=False)
    try:
        session_id = login_apex(driver, LOGIN_URL, USERNAME, PASSWORD)
        # Собираем универсальный URL
        target_url = build_apex_url(APP_ID, PAGE_ID, session_id)
        print("→ Переход на:", target_url)

        driver.get(target_url)
        wait_for_ready(driver)
        params = pandas.read_excel('params.xlsx')
        params = params.map(
            lambda x: (
                x.strftime("%d.%m.%Y %H:%M:%S") if isinstance(x, pandas.Timestamp)
                else str(int(x)) if isinstance(x, float) and x.is_integer()
                else str(x)
            )
        )
        params.fillna(0)
        for index, row, in params.iterrows():
            iot_id = row['Iot Id']
            date = row['Дата']
            offset = (row["Смещение"])#input
            driver_param = row["Водитель"]#input
            driver_tag = row["Тип Водителя"]#select
            trailer_param = row["Прицеп"]#input
            trailer_tag = row["Тип Прицепа"]#select
            param_key = row["Параметр Ключа"]#select
            voltage_key = row["Ключ напряжения"]#input
            ignition_param = row["Порог Зажигания"]#input
            stop_time = row["Время Остановки"]#input
            idle_work = row["Работа на холостом ходу"]#select
            satellite_param = row["Параметр Спутников"]#input
            satellite_count = row["Кол-во Спутников"]#input
            max_msg_distance = row["Макс Расстояние между сообщениями"]#input
            min_speed = row["Мин скорость"]#input
            min_trip_distance = row["Мин расстояние поездки"]#input
            signal_loss_interval = row["Интервал потери связи"]#input

            try:
                wait_for_element(driver, By.XPATH, "//button[contains(., 'Iot Id')]")
                find_and_click(driver, By.XPATH, "//button[contains(., 'Iot Id')]")
                find_and_input(driver, By.CLASS_NAME, 'apex-item-text', f'{iot_id}')  # Input Iot ID
                find_and_click(driver, By.XPATH, "//button[contains(., 'Применить')]")  # Search button with text Применить
            except:
                # Пример поиска и клика
                find_and_click(driver, By.ID, "R521054681622958314_actions_button")  # Actions
                # time.sleep(3)
                find_and_click(driver, By.XPATH, "//li[contains(., 'Фильтр')]")  # Filter with Iot ID
                find_and_input(driver, By.CLASS_NAME, 'apex-item-text', f'{iot_id}')  # Input Iot ID
                find_and_click(driver, By.XPATH, "//button[contains(., 'Применить')]")  # Search button with text Применить
                time.sleep(1)

            find_and_click(driver, By.XPATH, f"//a[contains(@href, '{iot_id}')]")  # Open object params
            to_frame(driver)  # Go to modal window
            # Main Params
            wait_for_element(driver, By.XPATH, "//*[contains(@name, 'START_DATE')]", 40)
            find_and_input(driver, By.XPATH, "//*[contains(@name, 'START_DATE')]", f'{date}')
            if offset!= 'nan':
                find_and_input(driver, By.NAME, fields_dict['Смещение'], f'{offset}')
            time.sleep(1)
            # driver/trailer
            find_and_click(driver, By.XPATH, "//*[contains(text(), 'Водитель/Прицеп')]")
            if driver_param != 'nan':
                find_and_input(driver, By.ID, fields_dict['Водитель'], driver_param)
            if driver_tag != 'nan':
                select_elem(driver, By.ID, fields_dict['Тип Водителя'], driver_tag)
            if trailer_param != 'nan':
                find_and_input(driver, By.ID, fields_dict['Прицеп'], trailer_param)
            if trailer_tag != 'nan':
                select_elem(driver, By.ID, fields_dict['Тип Прицепа'], trailer_tag)
            #motion params
            find_and_click(driver, By.XPATH, "//*[contains(text(), 'Настройки движения')]")
            if param_key != 'nan':
                select_elem(driver, By.ID, fields_dict['Параметр Ключа'], param_key)
            if voltage_key != 'nan':
                find_and_input(driver, By.ID, fields_dict['Ключ напряжения'], voltage_key)
            if ignition_param != 'nan':
                find_and_input(driver, By.ID, fields_dict['Порог Зажигания'], ignition_param)
            if stop_time != 'nan':
                find_and_input(driver, By.ID, fields_dict['Время Остановки'], stop_time)
            if idle_work != 'nan':
                select_elem(driver, By.ID, fields_dict['Работа на холостом ходу'], idle_work)
            if satellite_param != 'nan':
                find_and_input(driver, By.ID, fields_dict['Параметр Спутников'], satellite_param)
            if satellite_count != 'nan':
                find_and_input(driver, By.ID, fields_dict['Кол-во Спутников'], satellite_count)
            if max_msg_distance != 'nan':
                find_and_input(driver, By.ID, fields_dict['Макс Расстояние между сообщениями'], max_msg_distance)
            if min_speed != 'nan':
                find_and_input(driver, By.ID, fields_dict['Мин скорость'], min_speed)
            if min_trip_distance != 'nan':
                find_and_input(driver, By.ID, fields_dict['Мин расстояние поездки'], min_trip_distance)
            if signal_loss_interval != 'nan':
                find_and_input(driver, By.ID, fields_dict['Интервал потери связи'], signal_loss_interval)
            time.sleep(0.5)
            try:
                find_and_click(driver, By.ID, 'B427264443942920022')
            except:
                find_and_click(driver, By.ID, 'B427264897796920023')
            driver.switch_to.default_content()  # Go to main window
            wait_for_ready(driver, 180)

    finally:
        pass
        # driver.quit()
