import json
import re
import time
from time import sleep
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
from selenium.webdriver.common.action_chains import ActionChains


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
    base = "https://fms.smartagro.ru/ords/"
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
def js_click(driver, by, value, timeout=10):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    driver.execute_script("arguments[0].click();", el)
    return el


############################
# Пример использования
############################
if __name__ == "__main__":
    LOGIN_URL = "https://fms.smartagro.ru/ords/f?p=901:LOGIN::::::"
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
            date_from = row['От']
            date_to = (row["До"])#input
            ld = row['Действие']
            print(iot_id)

            try:
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
            wait_for_element(driver, By.XPATH, "//*[contains(@name, 'START_DATE')]")
            sleep(1)
            find_and_click(driver, By.XPATH, "//*[contains(text(), 'Параметры в ТС')]")
            js_click(driver, By.XPATH, "//li[a/span[text()='Параметры в ТС']]/a")
            sleep(0.5)
            if ld == 'з':
                find_and_click(driver, By.ID, "B427299884259920058")
                # to_frame(driver)
                find_and_input(driver, By.NAME, 'P702_IMPORT_START_TIME', date_from)
                find_and_input(driver, By.NAME, 'P702_IMPORT_END_TIME', date_to)
                time.sleep(0.5)
                find_and_click(driver, By.ID, "yes_import")
                WebDriverWait(driver, 2400).until(EC.invisibility_of_element_located((By.CLASS_NAME, "u-Processing-spinner")))
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                driver.switch_to.default_content()  # Go to main window
                time.sleep(3)
            elif ld == 'у':
                find_and_click(driver, By.ID, "B427300295346920058")
                # to_frame(driver)
                find_and_input(driver, By.NAME, 'P702_DELETE_START_TIME', date_from)
                find_and_input(driver, By.NAME, 'P702_DELETE_END_TIME', date_to)
                find_and_click(driver, By.ID, "yes_delete_message")
                WebDriverWait(driver, 2400).until(EC.invisibility_of_element_located((By.CLASS_NAME, "u-Processing-spinner")))
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.ESCAPE)
                    body.send_keys(Keys.ESCAPE)
                finally:
                    driver.switch_to.default_content()  # Go to main window
                    time.sleep(3)

    finally:
        pass
        # driver.quit()
