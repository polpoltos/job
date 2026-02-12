import re
import time
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, UnexpectedTagNameException

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
# Ожидания APEX
############################
def wait_apex(driver, timeout=20):
    """Ждём, пока APEX закончит AJAX-запросы"""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return (window.apex && apex.jQuery && apex.jQuery.active == 0)")
    )


############################
# Авторизация и работа с сессией
############################
def login_apex(driver, login_url, username, password):
    driver.get(login_url)
    wait_for_ready(driver)

    user_input = driver.find_element(By.ID, "P101_USERNAME")
    pass_input = driver.find_element(By.ID, "P101_PASSWORD")
    submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Войти в систему')]")

    user_input.clear()
    user_input.send_keys(username)
    pass_input.clear()
    pass_input.send_keys(password)
    submit_btn.click()

    wait_for_ready(driver)
    time.sleep(2)

    session_id = extract_apex_session(driver.current_url)
    if not session_id:
        raise RuntimeError("Не удалось определить session_id после логина")

    print(f"[INFO] Авторизация успешна, session_id = {session_id}")
    return session_id


def extract_apex_session(url: str) -> str | None:
    match = re.search(r"f\?p=\d+:\d+:(\d+):", url)
    return match.group(1) if match else None


def build_apex_url(app_id: int, page_id: int, session_id: str, params: str = "") -> str:
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


def js_click(driver, by, value, timeout=10):
    """Надёжный клик для Oracle APEX"""
    el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )
    driver.execute_script("arguments[0].click();", el)
    return el


def find_and_input(driver, by, search, value, timeout=10):
    click = driver.find_element(by, search)
    click.clear()
    click.send_keys(value)
    click.send_keys(Keys.ENTER)
    return click


def to_frame(driver):
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.switch_to.frame(iframe)


def back_frame(driver):
    driver.switch_to.default_content()


def select_elem(driver, by, search, text, log=True):
    try:
        element = driver.find_element(by, search)
        select = Select(element)

        matched_option = None
        for opt in select.options:
            if text.lower() in opt.text.strip().lower():
                matched_option = opt
                break

        if not matched_option:
            if log:
                print(f"[!] Не найдено ни одной опции, содержащей '{text}'")
            return False

        if matched_option.is_selected():
            if log:
                print(f"[✓] Опция '{matched_option.text}' уже выбрана.")
            return True

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
# Основной сценарий
############################
if __name__ == "__main__":
    LOGIN_URL = f"{base_url}/ords/f?p=901:LOGIN::::::"
    USERNAME = "salikov_z"
    PASSWORD = "1111"
    date_from = "21.10.2025"
    days = 10

    APP_ID = 901
    PAGE_ID = 458

    driver = create_browser(headless=False)

    try:
        session_id = login_apex(driver, LOGIN_URL, USERNAME, PASSWORD)

        target_url = build_apex_url(APP_ID, PAGE_ID, session_id)
        print("→ Переход на:", target_url)

        driver.get(target_url)
        wait_for_ready(driver)

        # Ввод даты
        find_and_input(driver, By.NAME, 'P458_DATE', date_from)
        for _ in range(days):
            wait_apex(driver)
            while True:
                wait_apex(driver)
                # Ищем все замки
                locks = driver.find_elements(By.CSS_SELECTOR, "a[title='Закрыт']")

                if not locks:
                    break

                js_click(driver, By.CSS_SELECTOR, "a[title='Закрыт']")

                to_frame(driver)
                wait_apex(driver)

                js_click(driver, By.XPATH, "//button[.//span[text()='Открыть']]")

                back_frame(driver)

                WebDriverWait(driver, 60).until_not(
                    EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                )

                wait_apex(driver)

            js_click(driver, By.CSS_SELECTOR, "i.fa-angle-left")


    finally:
        pass
        # driver.quit()
