import requests, json
import pandas as pd
from io import BytesIO
from vk_token import vk_token, group_id

# 🔑 Твой токен (замени на свой)
VK_ACCESS_TOKEN = vk_token

# 📌 ID группы (можно найти в URL сообщества или через поиск API)
GROUP_ID = group_id  # Внимание: для групп нужен минус перед ID!

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
    days_of_week = ['Понедельник', 'Вторник', 'Среда', 
                   'Четверг', 'Пятница', 'Суббота']
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
    """Форматирует данные одного дня."""
    lessons = []
    for i in range(0, len(day_data), 2):
        # Дополнительная фильтрация на случай пропущенных строк
        subject = day_data[i] if i < len(day_data) else ''
        details = day_data[i+1] if i+1 < len(day_data) else ''
        
        # Пропускаем ошибочные записи
        if any(keyword in subject for keyword in ["203 (ювелиры) (6)", "ювелиры", "(6)"]):
            continue
            
        lessons.append({
            'subject': subject,
            'details': details
        })
    
    return {
        'day_name': days_list[day_number] if day_number < len(days_list) else f'День {day_number+1}',
        'lessons': lessons
    }
    
def save_data_to_file(data, filename="output.txt"):
    """Записывает данные в текстовый или JSON файл"""
    if not data:
        print("Нет данных для записи!")
        return

    # Определяем формат по расширению файла
    file_format = filename.split('.')[-1].lower()

    if file_format == 'txt':
        # Сохранение в текстовый формат
        with open(filename, 'w', encoding='utf-8') as f:
            for schedule_block in data:
                # Заголовок блока
                f.write(f"Дата: {schedule_block['date_range']}\n")
                f.write(f"Группа: {schedule_block['group']}\n")
                f.write("=" * 50 + "\n\n")
                
                # Дни недели
                for day in schedule_block['days']:
                    f.write(f"{day['day_name'].upper()}\n")
                    f.write("-" * 50 + "\n")
                    
                    # Пары
                    for idx, lesson in enumerate(day['lessons'], 1):
                        f.write(f"{idx}. {lesson['subject']}\n")
                        if lesson['details']:
                            f.write(f"   {lesson['details']}\n")
                        f.write("\n")  # Разделитель между парами
                    
                    f.write("\n")  # Разделитель между днями
                
                f.write("\n\n")  # Разделитель между блоками

        print(f"Данные успешно сохранены в {filename}")

    elif file_format == 'json':
        # Сохранение в JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Данные успешно сохранены в {filename}")

    else:
        print(f"Неподдерживаемый формат файла: {file_format}")

# Основной процесс
xls_url = get_schedule_from_wall()
if xls_url:
    column_data = download_and_parse_xls(xls_url)
    save_data_to_file(column_data)
else:
    print("Файл не найден!")