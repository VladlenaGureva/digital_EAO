import pandas as pd
import json
import os
from collections import defaultdict

# Загружаем данные
df_routes = pd.read_excel('Датасет(АвтоматическиВосстановлено).xlsx', sheet_name='routes', engine='openpyxl')

# Группировка по (start_place_id, end_place_id, layer)
groups = defaultdict(list)
for _, row in df_routes.iterrows():
    key = (row['start_place_id'], row['end_place_id'], row['layer'])
    fragment = {
        "speaker": row.get('speaker', ''),
        "subtitle": row.get('subtitle', ''),
        "quote": row.get('quote', ''),
        "audio_url": row.get('audio_url', '')
    }
    groups[key].append(fragment)

os.makedirs('routes', exist_ok=True)

for (start_id, end_id, layer), fragments in groups.items():
    # Получаем русские названия из первой строки группы (они одинаковы для всех маршрутов с одинаковыми id)
    # Берем первую встреченную строку с этими start_id и end_id, чтобы извлечь start_rus_name, end_rus_name
    row_sample = df_routes[(df_routes['start_place_id'] == start_id) & (df_routes['end_place_id'] == end_id)].iloc[0]
    start_rus = row_sample.get('start_rus_name', start_id)
    end_rus = row_sample.get('end_rus_name', end_id)
    
    group_id = f"{start_id}→{end_id}_{layer}"
    safe_file_name = f"{start_id}_to_{end_id}_{layer}.json"
    # Читаемое название маршрута - русские названия, без указания слоя
    display_name = f"{start_rus} → {end_rus}"
    
    data = {
        "group_id": group_id,
        "name": display_name,
        "wave": layer,
        "start_id": start_id,
        "end_id": end_id,
        "start_name_ru": start_rus,
        "end_name_ru": end_rus,
        "short_history": "",
        "audio_fragments": fragments,
        "photos": []
    }
    with open(f'routes/{safe_file_name}', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Создано JSON для {len(groups)} групп маршрутов в папке routes/")