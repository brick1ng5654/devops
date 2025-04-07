import requests
import pandas as pd
from io import BytesIO
import json
from vk_token import vk_token, group_id

# 🔑 Твой токен и ID группы
VK_ACCESS_TOKEN = vk_token
GROUP_ID = group_id  # Для групп нужен минус перед ID!
API_VERSION = "5.131"

def get_schedule_from_wall():
    """Ищет ссылку на xls-файл в постах группы."""
    url = "https://api.vk.com/method/wall.get"
    params = {
        "owner_id": f"-{GROUP_ID}",
        "count": 10,  # Проверяем 10 последних постов
        "access_token": VK_ACCESS_TOKEN,
        "v": API_VERSION
    }
    
    response = requests.get(url, params=params).json()
    
    if "response" in response and "items" in response["response"]:
        for post in response["response"]["items"]:
            if "attachments" in post:
                for attachment in post["attachments"]:
                    if attachment["type"] == "doc" and attachment["doc"]["ext"] in ["xls", "xlsx"]:
                        print(f"Найден файл: {attachment['doc']['title']}")
                        return attachment["doc"]["url"]
    
    return None

def download_and_parse_xls(url):
    """Скачивает и парсит xls-файл с разделением на дни недели."""
    response = requests.get(url)
    if response.status_code != 200:
        return None

    # Читаем Excel и извлекаем данные
    try:
        df = pd.read_excel(BytesIO(response.content), sheet_name="  2 инст.")
        column_data = df.iloc[:, 4].fillna('<<EMPTY>>').astype(str).tolist()
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return None

    # Параметры для парсинга
    schedule = []
    days_of_week = ['ПОНЕДЕЛЬНИК', 'ВТОРНИК', 'СРЕДА', 'ЧЕТВЕРГ', 'ПЯТНИЦА', 'СУББОТА']
    current_group = None
    current_date = None
    current_day = []
    day_counter = 0

    for item in column_data:
        item = item.strip().replace('<<EMPTY>>', '')
        
        # Пропускаем строку с информацией о группе в теле расписания
        if "203 (ювелиры) (6)" in item and not ('-' in item and '.' in item):
            continue
            
        # Обнаружение нового блока расписания
        if '-' in item and '.' in item:
            if current_date is not None:
                # Сохраняем последний день предыдущего блока
                if current_day:
                    schedule[-1]['days'].append(process_day(current_day, day_counter, days_of_week))
            
            # Новый блок расписания
            parts = item.split('\n')
            schedule.append({
                'date_range': parts[0],
                'group': parts[1] if len(parts) > 1 else '',
                'days': []
            })
            current_date = parts[0]
            day_counter = 0
            current_day = []
            continue
            
        # Разделитель дней
        if not item:
            if current_day:
                schedule[-1]['days'].append(process_day(current_day, day_counter, days_of_week))
                day_counter += 1
                current_day = []
            continue
            
        current_day.append(item)

    # Обработка последнего дня
    if current_day:
        schedule[-1]['days'].append(process_day(current_day, day_counter, days_of_week))

    return schedule

def process_day(day_data, day_number, days_list):
    """Форматирует данные одного дня в список уроков."""
    lessons = []
    for i in range(0, len(day_data), 2):
        # Дополнительная фильтрация на случай пропущенных строк
        subject = day_data[i] if i < len(day_data) else ''
        details = day_data[i+1] if i+1 < len(day_data) else ''
        
        # Пропускаем ошибочные записи
        if any(keyword in subject for keyword in ["203 (ювелиры) (6)", "ювелиры", "(6)"]):
            continue
            
        if subject and details:  # Убеждаемся, что есть и предмет, и детали
            lessons.append(f"{subject} - {details}")
    
    return {
        'day_name': days_list[day_number] if day_number < len(days_list) else f'ДЕНЬ_{day_number+1}',
        'lessons': lessons
    }

def save_data_to_json(data, filename="schedule.json"):
    """Сохраняет данные в JSON-формате для Home Assistant."""
    if not data:
        print("Нет данных для записи!")
        return

    # Создаем структуру JSON
    json_data = {
        "date": data[0]['date_range'],  # Берем дату из первого блока
        "group": data[0]['group'],      # Берем группу из первого блока
        "schedule": {}
    }

    # Заполняем расписание по дням
    for block in data:
        for day in block['days']:
            json_data["schedule"][day['day_name']] = day['lessons']

    # Сохранение в JSON-файл
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"Данные успешно сохранены в {filename}")

# Основной процесс
xls_url = get_schedule_from_wall()
if xls_url:
    column_data = download_and_parse_xls(xls_url)
    save_data_to_json(column_data, "schedule.json")
else:
    print("Файл не найден!")