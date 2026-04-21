import time

import requests
import json

base_url = 'http://93.90.221.111:4298'

def get_tech(domain, username):
    data_tech = {'domain': domain, 'username': username}
    response = requests.get(base_url + '/v1/tech', params=data_tech)
    techs = [tech.get('remote_id') for tech in response.json()]
    return techs


def get_params(domain, username, password, remote_id):
    data_param = {
        'domain': domain,
        'username': username,
        'password': password,
        'remote_id': remote_id
    }
    try:
        response = requests.get(base_url + '/v1/sensors', params=data_param)
        if response.status_code != 200:
            print(f"Ошибка get_params (remote_id={remote_id}): статус {response.status_code}, текст: {response.text}")
            return []
        data = response.json()
        # Если ответ — не список, пробуем преобразовать в список
        if isinstance(data, list):
            return data
        else:
            print(f"Неожиданный формат ответа для remote_id={remote_id}: {type(data)}")
            # Если это словарь, можно обернуть в список или вернуть пустой
            return []
    except json.JSONDecodeError:
        print(f"Ошибка парсинга JSON в get_params (remote_id={remote_id}), ответ: {response.text}")
        return []
    except Exception as e:
        print(f"Исключение в get_params (remote_id={remote_id}): {e}")
        return []

def mapp_param(domain, username, param_type, remote_id, value):
    data_map = {
        'domain': domain,
        'username': username,
        'type': param_type,           # переименовано, чтобы не конфликтовать с type()
        'object_remote_id': remote_id,
        'value': value
    }
    headers = {
        "accept": "*/*",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(base_url + '/v1/responseParameter',headers=headers, json=data_map)
        if response.status_code != 200:
            print(f"Ошибка mapp_param: статус {response.status_code}, текст: {response.text}")
            return None
    except Exception as e:
        print(f"Исключение в mapp_param: {e}")
        return None

if __name__ == '__main__':
    domain = 'https://glonass.m2m-sib.ru'
    username = 'manasmartagro'
    password = 'Abc12345!'
    counter = 0
    tech_ids = get_tech(domain, username)
    print(f"Получено устройств: {len(tech_ids)}")
    print(tech_ids)

    for remote_id in tech_ids:
        counter += 1
        try:
            # Получаем параметры один раз для текущего remote_id
            params = get_params(domain, username, password, remote_id)
            if not params:
                continue
            # Ищем нужные параметры в списке
            voltage = next(
                (str(item.get('id')) for item in params if 'напряж' in item.get('name', '').lower()),
                None
            )
            fuel = next(
                (str(item.get('id')) for item in params if 'топливо' in item.get('name', '').lower()),
                None
            )
            uss = next(
                (str(item.get('id')) for item in params if 'выдача' in item.get('name', '').lower()),
                None
            )

            print(f"{counter} remote_id={remote_id}, fuel={fuel}, voltage={voltage}, uss={uss}")

            # if voltage:
            #     mapp_param(domain, username, 8, remote_id, voltage)
            if fuel:
                mapp_param(domain, username, 0, remote_id, fuel)
                print('Смапплено')
            time.sleep(2)
            # if uss:
            #     mapp_param(domain, username, 7, remote_id, uss)

        except Exception as e:
            print(f"Ошибка при обработке remote_id={remote_id}: {e}")
