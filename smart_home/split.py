import pandas as pd

# Загрузка данных из Excel
df = pd.read_excel('output.xlsx', header=None)
column_data = df.iloc[:, 4].tolist()

# Преобразование данных и удаление пустых строк
cleaned_data = []
for item in column_data:
    if pd.notna(item) and str(item).strip() != '':
        cleaned_data.append(str(item).strip())

# Группировка по дням (разделитель - строка с датой)
days = []
current_day = []
for item in cleaned_data:
    if '-' in item and '.' in item and len(item.split('-')) == 2:  # Проверка на дату
        if current_day:
            days.append(current_day)
        current_day = [item]
    else:
        current_day.append(item)
if current_day:
    days.append(current_day)

# Обработка каждой группы данных
formatted_schedule = []
for day in days:
    # Извлечение даты и группы
    header = day[0].split('\n')
    date_range = header[0]
    group_info = header[1] if len(header) > 1 else ''
    
    formatted_schedule.append(f"Дата: {date_range}")
    formatted_schedule.append(f"Группа: {group_info}")
    
    # Обработка пар
    lessons = []
    for i in range(1, len(day)):
        if i % 2 != 0:
            lesson = {
                'subject': day[i],
                'details': day[i+1] if i+1 < len(day) else ''
            }
            lessons.append(lesson)
    
    # Форматирование вывода
    for idx, lesson in enumerate(lessons, 1):
        formatted_schedule.append(f"{idx}. {lesson['subject']}")
        formatted_schedule.append(f"   {lesson['details']}")
    
    formatted_schedule.append("\n" + "="*50 + "\n")

# Вывод результата
print('\n'.join(formatted_schedule))