import pandas as pd
import json
from collections import defaultdict

# Загружаем листы
df_places = pd.read_excel('Датасет(АвтоматическиВосстановлено).xlsx', sheet_name='places', engine='openpyxl')
df_routes = pd.read_excel('Датасет(АвтоматическиВосстановлено).xlsx', sheet_name='routes', engine='openpyxl')

# Словарь координат: place_id -> (lon, lat)
coords = {}
for _, row in df_places.iterrows():
    place_id = row['place_id']
    lon = float(row['longitude'])
    lat = float(row['latitude'])
    coords[place_id] = (lon, lat)

# Группировка по (start_place_id, end_place_id, layer)
groups = defaultdict(list)  # key -> list of route_id
for _, row in df_routes.iterrows():
    start = row['start_place_id']
    end = row['end_place_id']
    layer = row['layer']
    key = (start, end, layer)
    groups[key].append(row['route_id'])

# Формируем FeatureCollection
features = []
for (start_id, end_id, layer), route_ids in groups.items():
    if start_id not in coords or end_id not in coords:
        print(f"Пропущена группа {start_id}->{end_id}: нет координат")
        continue
    # Берём название маршрута из первой строки (можно заменить на осмысленное)
    first_route = df_routes[df_routes['route_id'] == route_ids[0]].iloc[0]
    name = f"{first_route['start_place_id']} → {first_route['end_place_id']} ({layer})"
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [list(coords[start_id]), list(coords[end_id])]
        },
        "properties": {
            "group_id": f"{start_id}->{end_id}_{layer}",
            "name": name,
            "wave": layer,
            "route_ids": route_ids  # список оригинальных route_id
        }
    }
    features.append(feature)

geojson = {"type": "FeatureCollection", "features": features}
with open('routes.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print(f"Сохранено {len(features)} групп маршрутов в routes.geojson")