import pandas as pd
import json
import os
from collections import defaultdict

df_places = pd.read_excel('Датасет.xlsx', sheet_name='places', engine='openpyxl')
df_audio = pd.read_excel('Датасет.xlsx', sheet_name='audio', engine='openpyxl')
df_photo = pd.read_excel('Датасет.xlsx', sheet_name='photo', engine='openpyxl')

output_dir = 'places'
os.makedirs(output_dir, exist_ok=True)

layer_col = 'layer'

audio_by_place = defaultdict(lambda: defaultdict(list))
for _, row in df_audio.iterrows():
    place_id = row['place_id']
    layer = row[layer_col]
    if pd.isna(layer) or not layer:
        continue
    narrative = {}
    if pd.notna(row.get('speaker')):
        narrative['speaker'] = row['speaker']
    if pd.notna(row.get('subtitle')):
        narrative['subtitle'] = row['subtitle']
    if pd.notna(row.get('quote')):
        narrative['quote'] = row['quote']
    if pd.notna(row.get('audio_url')):
        narrative['audio_url'] = row['audio_url'].strip()
    if narrative:
        audio_by_place[place_id][layer].append(narrative)

photo_by_place = defaultdict(list)
for _, row in df_photo.iterrows():
    place_id = row['place_id']
    photo = {}
    if pd.notna(row.get('caption')):
        photo['caption'] = row['caption']
    if pd.notna(row.get('source')):
        photo['source'] = row['source']
    if pd.notna(row.get('photo_url')):
        photo['url'] = row['photo_url'].strip()
    if photo:
        photo_by_place[place_id].append(photo)

for _, row in df_places.iterrows():
    place_id = row['place_id']
    name = row['name_place'] if pd.notna(row['name_place']) else place_id
    short_history = row['short_text'] if pd.notna(row['short_text']) else ""

    layers = list(audio_by_place[place_id].keys()) if place_id in audio_by_place else []
    default_tab = layers[0] if layers else None

    tabs = {}
    if place_id in audio_by_place:
        for layer, narratives in audio_by_place[place_id].items():
            label = layer.replace('_', ' ').title()
            tabs[layer] = {
                "label": label,
                "historical_note": "",
                "narratives": narratives
            }

    photos = photo_by_place[place_id] if place_id in photo_by_place else []

    place_data = {
        "place_id": place_id,
        "name": name,
        "short_history": short_history,
        "layers": layers,
        "default_tab": default_tab,
        "tabs": tabs,
        "photos": photos
    }

    output_file = os.path.join(output_dir, f"{place_id}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(place_data, f, ensure_ascii=False, indent=2)

print(f"JSON-файлы для мест сохранены в папку {output_dir}")
