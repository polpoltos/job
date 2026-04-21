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



from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ApexIG:
    def __init__(self, driver, grid_id, timeout=20):
        self.driver = driver
        self.grid_id = grid_id
        self.timeout = timeout

    def _find_header_and_col_id(self, column_name):
        headers = self.driver.find_elements(
            By.CSS_SELECTOR,
            f"#{self.grid_id} .a-GV-hdr table thead tr.a-GV-row th"
        )

        for i, th in enumerate(headers):
            try:
                label_el = th.find_element(By.CSS_SELECTOR, ".a-GV-headerLabel")
                text = label_el.text.strip()
            except:
                continue

            if column_name.lower() in text.lower():
                hdr_id = label_el.get_attribute("id")
                base_id = hdr_id.replace("_HDR", "") if hdr_id else None
                return i, base_id

        raise Exception(f"Колонка '{column_name}' не найдена")

    def _get_row(self):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"#{self.grid_id} .a-GV-table tbody tr.is-inserted")
            )
        )

    def set(self, column_name: str, value: str):
        header_index, col_base_id = self._find_header_and_col_id(column_name)
        td_index = header_index - 1

        row = self._get_row()
        tds = row.find_elements(By.CSS_SELECTOR, "td.a-GV-cell")

        if td_index < 0 or td_index >= len(tds):
            raise Exception(f"td_index={td_index}, td_count={len(tds)}")

        cell = tds[td_index]

        # 1. Клик по ячейке
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cell)
        self.driver.execute_script("arguments[0].click();", cell)

        # 2. ENTER для активации редактора
        cell.send_keys(Keys.ENTER)

        # 3. Пытаемся найти редактор внутри ячейки
        def find_editor_in_cell():
            try:
                return cell.find_element(By.CSS_SELECTOR, "input, textarea")
            except:
                return None

        editor = None

        # 4. Ждём появления редактора в ячейке
        try:
            editor = WebDriverWait(self.driver, self.timeout).until(
                lambda d: find_editor_in_cell()
            )
        except:
            pass

        # 5. Если редактор не появился — пробуем columnItemContainer
        if editor is None:
            try:
                editor = self.driver.find_element(
                    By.CSS_SELECTOR,
                    f".a-GV-columnItemContainer input#{col_base_id}"
                )
            except:
                pass

        # 6. Если всё ещё нет — двойной клик и повтор
        if editor is None:
            self.driver.execute_script("arguments[0].click();", cell)
            self.driver.execute_script("arguments[0].click();", cell)
            editor = find_editor_in_cell()

        if editor is None:
            raise Exception(f"Не удалось активировать редактор для '{column_name}'")

        # 7. Вводим значение
        editor.send_keys(Keys.CONTROL, "a")
        editor.send_keys(value)
        editor.send_keys(Keys.TAB)

    def save(self):
        """
        Нажимает кнопку 'Сохранить' в тулбаре IG.
        """

        # Правильный тулбар — без _grid_vc
        toolbar_id = self.grid_id.replace("_grid_vc", "_toolbar")

        save_btn = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f"#{toolbar_id} [data-action='save']"
            ))
        )

        # Кликаем через JS
        self.driver.execute_script("arguments[0].click();", save_btn)

        # Ждём завершения сохранения
        WebDriverWait(self.driver, self.timeout).until_not(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, f"#{self.grid_id}_status"),
                "Сохранение"
            )
        )




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
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))

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

def switch_to_iframe_with_element(driver, by, value, timeout=10):
    driver.switch_to.default_content()
    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    for iframe in iframes:
        driver.switch_to.default_content()
        driver.switch_to.frame(iframe)
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((by, value)))
            return True
        except:
            pass

    raise Exception(f"Элемент {value} не найден ни в одном iframe")

def js_click(driver, by, value, timeout=10):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    driver.execute_script("arguments[0].click();", el)
    return el

import tempfile
import os

def upload_existing_csv(driver, file_input_id: str, csv_path: str, timeout=10):
    file_input = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, file_input_id))
    )
    file_input.send_keys(os.path.abspath(csv_path))

def upload_csv_to_apex(
    driver,
    file_input_id: str,
    rows: list[list[int | str]],
    header: list[str] | None = None,
    upload_button_xpath: str | None = None,
    timeout: int = 10
):
    """
    Загружает CSV файл в Oracle APEX через <input type="file">

    :param driver: Selenium WebDriver
    :param file_input_id: ID input[type=file], например 'P515_CSV_TAB'
    :param rows: данные CSV, например [[1,1],[2000,2000]]
    :param header: заголовок CSV, например ['X','Y']
    :param upload_button_xpath: XPath кнопки 'Загрузить' / 'Импортировать' (если нужна)
    """

    # 1. Создаём временный CSV
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv",
        mode="w",
        encoding="utf-8",
        newline=""
    ) as f:
        if header:
            f.write(",".join(header) + "\n")
        for row in rows:
            f.write(",".join(str(v) for v in row) + "\n")
        csv_path = f.name

    # 2. Ждём input file
    file_input = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, file_input_id))
    )

    # 3. Загружаем файл (ФОНОВО)
    file_input.send_keys(csv_path)

    # 4. Нажимаем кнопку импорта (если есть)
    if upload_button_xpath:
        upload_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, upload_button_xpath))
        )
        upload_btn.click()

    return csv_path  # путь можно удалить потом при желании


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
            date = row['Дата']
            dut = (row["ДУТы"])  # input
            min_zapr = row["Мин заправка"]  # input
            min_sliv = row["Мин слив"]  # select
            ignor_soob = row["Игнор сооб"]  # input
            min_ostanovka = row["Мин остановка"]  # select
            timeout_zapr = row["Таймаут заправок"]  # select
            timeout_sliv = row["Таймаут Сливов"]  # input
            stop_zapr = row["Заправки на остановке"]  # input
            max_speed = row["Макс скорость"]  # input
            timeout_buk = row["Таймаут бака"]  # select
            messages = row["Сообщения"]  # input
            voltage = row["Напряжение"]  # input
            norma = row["Норма расхода"]  # input
            akb = row["АКБ на массу"]  # input


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
            wait_for_ready(driver)
            switch_to_iframe_with_element(driver, By.XPATH, "//*[contains(@name, 'START_DATE')]")  # Go to modal window
            # Main Params
            sleep(1.5)
            js_click(driver, By.XPATH, "//li[a/span[text()='Топливо']]/a") #ПОФИКСИТЬ КЛИК НЕ ВСЕГДА ПРОХОДИТ
            sleep(0.5)

            if dut == 'Да':
                js_click(driver, By.ID, "B427330460014920078")
                switch_to_iframe_with_element(driver, By.ID, 'P515_START_DATE')
                find_and_input(driver, By.ID, 'P515_START_DATE', date)
                grid_duts = ApexIG(driver, "duts_new_ig_grid_vc")

                grid_duts.set("параметр датчика", "fuel0")
                grid_duts.set("параметр из сообщения", "fuelSensorValue")
                grid_duts.set("минимальное значение датчика", "1")
                grid_duts.set("максимальное значение датчика", "2000")
                grid_duts.save()
                time.sleep(1)
                grid_cal = ApexIG(driver, "cal_tab_new_ig_grid_vc")
                upload_existing_csv(
                    driver,
                    "P515_CSV_TAB",
                    r"C:\calibr\table.csv"
                )
                grid_cal.save()
                switch_to_iframe_with_element(driver, By.ID, 'B428166919717409101')
                js_click(driver, By.ID, 'B428166919717409101')
                time.sleep(2)
                switch_to_iframe_with_element(driver, By.CSS_SELECTOR, 'td.a-IRR-linkCol a')
                js_click(driver, By.CSS_SELECTOR, 'td.a-IRR-linkCol a')

                switch_to_iframe_with_element(driver, By.ID, 'B428176807964409109')
                js_click(driver, By.ID, 'B428176807964409109')

                switch_to_iframe_with_element(driver, By.ID, 'B427330862245920078')
                js_click(driver, By.ID, 'B427330862245920078')
            sleep(2)
            find_and_click(driver, By.XPATH, "//button[span[text()='создать настройки топлива']]")
            wait_for_ready(driver)
            switch_to_iframe_with_element(driver, By.ID, 'P518_TIME')
            find_and_input(driver, By.ID, 'P518_TIME', f'{date}')
            if min_zapr != 'nan':
                find_and_input(driver, By.ID, 'P518_MIN_REFUELING_VOLUME', f'{min_zapr}')
            if min_sliv != 'nan':
                find_and_input(driver, By.ID, 'P518_MIN_DRAIN_VOLUME', f'{min_sliv}')
            if ignor_soob != 'nan':
                find_and_input(driver, By.ID, 'P518_TIMEOUT_AFTER_START_MOTION', f'{ignor_soob}')
            if min_ostanovka != 'nan':
                find_and_input(driver, By.ID, 'P518_MIN_STOP_TIME_FOR_DRAIN', f'{min_ostanovka}')
            if timeout_zapr != 'nan':
                find_and_input(driver, By.ID, 'P518_TIMEOUT_FOR_SEPARATING_REFUELING', f'{timeout_zapr}')
            if timeout_sliv != 'nan':
                find_and_input(driver, By.ID, 'P518_TIMEOUT_FOR_SPLITTING_DRAINS', f'{timeout_sliv}')
            if stop_zapr == 'Да':
                find_and_click(driver, By.CSS_SELECTOR, "label[for='P518_SEARCH_REFUEL_ONLY_STOPPED_Y']")
                find_and_input(driver, By.ID, 'P518_MAX_SPEED_WHEN_STOP_FOR_REFUEL', f'{max_speed}')
            else:
                find_and_click(driver, By.CSS_SELECTOR, "label[for='P518_SEARCH_REFUEL_ONLY_STOPPED_N']")
            if timeout_buk != 'nan':
                find_and_input(driver, By.ID, 'P518_TIMEOUT_FOR_FULL_REFUEL', f'{timeout_buk}')
            if messages != 'nan':
                find_and_input(driver, By.ID, 'P518_COUNT_MESSAGES_FOR_FILTER', f'{messages}')
            if voltage != 'nan':
                find_and_input(driver, By.ID, 'P518_FUEL_LEVEL_SENSOR_VOLTAGE', f'{voltage}')
            if norma != 'nan':
                find_and_input(driver, By.ID, 'P518_IDLE_FUEL_CONSUMPTION', f'{norma}')
            if akb == 'Да':
                find_and_click(driver, By.CSS_SELECTOR, "label[for='P518_FUEL_BY_WEIGHT_Y']")
            else:
                find_and_click(driver, By.CSS_SELECTOR, "label[for='P518_FUEL_BY_WEIGHT_N']")
            js_click(driver, By.ID, "B428242432736455730")
            sleep(1)
            switch_to_iframe_with_element(driver, By.ID, 'B427326665613920075')
            js_click(driver, By.ID, 'B427326665613920075')
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            # body.send_keys(Keys.ESCAPE)
            driver.switch_to.default_content()  # Go to main window

    finally:
        pass
        # driver.quit()
