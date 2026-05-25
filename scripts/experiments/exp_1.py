import csv
import json
import re
from collections import defaultdict, Counter

PILOT_CSV = "places_with_codes_and_text (2).csv"
CODES_TXT = "code.txt"
OUTPUT_JSON = "dict.json"
THRESHOLD = 3  # слово должно встретиться хотя бы в THRESHOLD фрагментах

def clean_text(text):
    # Убираем знаки препинания, оставляем буквы, цифры, пробелы и дефисы
    text = re.sub(r"[^\w\s-]", "", text.lower())
    words = text.split()
    # Убираем слова короче 2 букв (предлоги, союзы)
    words = [w for w in words if len(w) > 1]
    return words

def main():
    # Загружаем список всех кодов
    with open(CODES_TXT, "r", encoding="utf-8") as f:
        all_codes = [line.strip() for line in f if line.strip()]
    
    # Словарь для сбора частот
    code_word_counts = {code: Counter() for code in all_codes}
    
    # Читаем пилотный CSV
    with open(PILOT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            codes_str = row.get("codes", "").strip()
            if not codes_str:
                continue
            # Коды разделены точкой с запятой (возможно с пробелами)
            codes = [c.strip() for c in codes_str.split(";") if c.strip()]
            text = row.get("text", "")
            if not text:
                continue
            words = clean_text(text)
            if not words:
                continue
            for code in codes:
                if code in code_word_counts:
                    code_word_counts[code].update(words)
    
    # Формируем словарь
    result_dict = {}
    for code, counter in code_word_counts.items():
        words = [word for word, cnt in counter.items() if cnt >= THRESHOLD]
        # Сортировка по убыванию частоты (полезно для отладки)
        words.sort(key=lambda w: counter[w], reverse=True)
        result_dict[code] = words
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"Словарь сохранён в {OUTPUT_JSON}")
    print(f"Всего кодов: {len(result_dict)}")
    for code, words in list(result_dict.items())[:5]:
        print(f"{code}: {words[:10]}...")

if __name__ == "__main__":
    main()
