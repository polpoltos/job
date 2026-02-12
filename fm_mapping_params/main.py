import requests
import json
import time
import openpyxl

url_cmt = 'https://fort.centr-tmt.ru'#Ввод
type_param = 0


def connect_to_api():
    """Функция подключения к API"""
    url = f"{url_cmt}/api/integration/v1/connect"
    params = {
        "login": "engineer145",#Ввод
        "password": "engineer145",#Ввод
        "lang": "ru-ru",
        "timezone": "3"#Ввод
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("Авторизация успешна!")
        return response.cookies
    else:
        print(f"Ошибка авторизации: {response.status_code}")
        return None


import requests
import time

def get_sensors(remote_id, cookies, max_retries=3, delay=2):
    """
    Получение сенсоров с использованием cookies.
    Добавлены:
      - таймаут
      - повторные попытки при ошибках
      - автообновление cookies при истечении сессии
    """
    url = f"{url_cmt}/api/integration/v1/objsensorslist"
    params = {"oid": str(remote_id)}

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, cookies=cookies, timeout=10)

            # если авторизация слетела → пробуем обновить cookies
            if response.status_code == 401:
                print("⚠️ Сессия устарела, пробуем переподключиться...")
                cookies = connect_to_api()
                if not cookies:
                    return None
                continue  # повторяем запрос с новыми cookies

            response.raise_for_status()  # выбросит ошибку при 4xx/5xx

            print("Данные сенсоров получены!")
            return response.json()

        except requests.exceptions.ConnectTimeout:
            print(f"⏳ Таймаут при подключении (попытка {attempt}/{max_retries})")
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при получении сенсоров (попытка {attempt}/{max_retries}): {e}")

        # ждём перед повтором
        time.sleep(delay * attempt)

    print("❌ Не удалось получить данные сенсоров после всех попыток")
    return None



def mapping(remote_id, name):
    time.sleep(1)
    url = "http://93.90.221.111:4292/v1/responseParameter"

    # ИСПРАВЛЕННЫЕ HEADERS - text/plain вместо application/json
    headers = {
        'accept': '*/*',
        'Content-Type': 'text/plain; charset=utf-8'  # ← ВАЖНО!
    }

    # Формируем данные как plain text
    data = f'{{"domain": "{url_cmt}", "type": {type_param}, "object_remote_id": "{remote_id}", "value": "{name}"}}'

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data.encode('utf-8'),  # Явно кодируем в bytes
            timeout=30
        )

        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")

        if response.status_code == 200:
            print("✅ Запрос выполнен успешно!")
        else:
            print(f"❌ Ошибка: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при выполнении запроса: {e}")


def read_excel(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    cookies = connect_to_api()
    bad_ids = []  # список для проблемных remote_id

    if cookies:
        for row in sheet.iter_rows(min_row=2, values_only=True):
            remote_id = str(row[0])
            print(f"Обрабатываем remote_id: {remote_id}")
            sensors_data = get_sensors(remote_id, cookies)

            # Проверяем, что данные получены и это словарь
            if sensors_data and isinstance(sensors_data, dict) and 'obj_sensors' in sensors_data:
                fuels = []
                for sensor in sensors_data['obj_sensors']:
                    if sensor.get('icon') == 'fuel.png':
                        fuels.append(sensor.get('name', ''))
                print(f"Найдены сенсоры: {fuels}")

                if fuels:
                    fuel_name = fuels[-1]
                    print(f"Отправляем значение: '{fuel_name}'")
                    mapping(remote_id, fuel_name)
                else:
                    print("Не найдено сенсоров с иконкой noicon.png")
            else:
                print(f"⚠️ Нет данных по сенсорам для {remote_id}")
                bad_ids.append(remote_id)




read_excel('New.xlsx')#Выбор файла формата xlsx