import csv
import json
from collections import defaultdict

INPUT_CSV = "all_coded.csv"
CODES_TXT = "code.txt"
OUTPUT_JSON = "tag_combination_stats.json"

def main():
    # Загружаем список допустимых семантических кодов
    with open(CODES_TXT, "r", encoding="utf-8") as f:
        valid_codes = set(line.strip() for line in f if line.strip())
    
    # Статистика: ключ (отсортированные теги через "|") -> {code: count}
    combo_stats = defaultdict(lambda: defaultdict(int))
    
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_tags = row.get("all_tags", "").strip()
            codes_str = row.get("codes", "").strip()
            if not all_tags or not codes_str:
                continue
            # Разделители: теги – запятая или точка с запятой
            tags = [t.strip() for t in all_tags.replace(';', ',').split(',') if t.strip()]
            codes = [c.strip() for c in codes_str.split(";") if c.strip()]
            codes = [c for c in codes if c in valid_codes]
            if not codes:
                continue
            tags.sort()
            key = "|".join(tags)
            for code in codes:
                combo_stats[key][code] += 1
    
    output = {key: dict(codes) for key, codes in combo_stats.items()}
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Статистика сочетаний тегов сохранена в {OUTPUT_JSON}")
    print(f"Всего уникальных комбинаций: {len(output)}")
    # Вывод первых 5 для примера
    for key, codes in list(output.items())[:5]:
        print(f"{key}: {dict(list(codes.items())[:5])}...")

if __name__ == "__main__":
    main()