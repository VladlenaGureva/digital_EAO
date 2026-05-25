import pandas as pd
import json

# Указываем engine='openpyxl' для работы с .xlsx
df_places = pd.read_excel('Датасет.xlsx', sheet_name='places', engine='openpyxl')
df_audio = pd.read_excel('Датасет.xlsx', sheet_name='audio', engine='openpyxl')

# Собираем уникальные слои для каждого place_id
layers_by_place = {}
for _, row in df_audio.iterrows():
    pid = row['place_id']
    layer = row['layer']
    if pid not in layers_by_place:
        layers_by_place[pid] = set()
    layers_by_place[pid].add(layer)

features = []
for _, row in df_places.iterrows():
    if pd.isna(row['longitude']) or pd.isna(row['latitude']):
        continue
    place_id = row['place_id']
    layers = list(layers_by_place.get(place_id, []))
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [float(row['longitude']), float(row['latitude'])]
        },
        "properties": {
            "place_id": place_id,
            "name": row['name_place'],
            "short_history": row['short_text'] if pd.notna(row['short_text']) else "",
            "layers": layers
        }
    }
    features.append(feature)

geojson = {"type": "FeatureCollection", "features": features}
with open('places.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print(f"GeoJSON сохранён: places.geojson, количество точек: {len(features)}")
