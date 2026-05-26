import csv
import json
import re
from collections import defaultdict, Counter
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

# Пути к файлам
INPUT_CSV = "places_with_codes_and_text (2).csv"       # файл со всеми размеченными интервью
CODES_TXT = "code.txt"           # список всех семантических кодов (один на строку)
OUTPUT_JSON = "dict_advanced.json"

# Стоп-слова (можно оставить из предыдущего варианта)
STOP_WORDS = set([
    "и", "в", "во", "на", "с", "со", "у", "к", "о", "об", "по", "из", "за", "от", "до", "при", "через",
    "а", "но", "да", "же", "ли", "бы", "вот", "это", "то", "там", "тут", "так", "как", "что", "когда",
    "где", "куда", "откуда", "зачем", "почему", "потому", "поэтому", "который", "такой", "этот", "тот",
    "быть", "стать", "являться", "говорить", "сказать", "знать", "видеть", "смотреть", "идти", "ехать",
    "весь", "вся", "всё", "все", "ещё", "уже", "только", "если", "чтобы", "также", "очень", "можно",
    "нужно", "надо", "будет", "было", "была", "были", "был", "нет", "да", "не", "ни", "или", "либо"
])

def clean_and_lemmatize(text):
    """Очистка, лемматизация, удаление стоп-слов, генерация униграмм и биграмм."""
    # Приводим к нижнему регистру и удаляем пунктуацию (оставляем буквы, цифры, дефисы, пробелы)
    text = re.sub(r"[^\w\s-]", "", text.lower())
    words = text.split()
    # Лемматизация и фильтрация
    lemmas = []
    for w in words:
        if w in STOP_WORDS or len(w) < 3:
            continue
        lemma = morph.parse(w)[0].normal_form
        if lemma not in STOP_WORDS and len(lemma) > 2:
            lemmas.append(lemma)
    # Биграммы (пары последовательных лемм)
    bigrams = []
    for i in range(len(lemmas)-1):
        bigram = lemmas[i] + " " + lemmas[i+1]
        bigrams.append(bigram)
    return lemmas + bigrams

def main():
    # Загружаем список всех кодов
    with open(CODES_TXT, "r", encoding="utf-8") as f:
        all_codes = [line.strip() for line in f if line.strip()]

    # Счётчики для каждого кода
    code_counters = {code: Counter() for code in all_codes}

    # Читаем CSV
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Предполагаем, что колонки называются "codes" и "text"
        for row in reader:
            codes_str = row.get("codes", "").strip()
            if not codes_str:
                continue
            codes = [c.strip() for c in codes_str.split(";") if c.strip()]
            text = row.get("text", "")
            if not text:
                continue
            tokens = clean_and_lemmatize(text)
            if not tokens:
                continue
            for code in codes:
                if code in code_counters:
                    code_counters[code].update(tokens)

    # Формируем итоговый словарь (все токены с частотами)
    result_dict = {}
    for code, counter in code_counters.items():
        # Можно оставить все слова, даже с частотой 1, но лучше отфильтровать шум
        filtered = {word: cnt for word, cnt in counter.items() if cnt >= 1}
        if filtered:
            result_dict[code] = filtered

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)

    print(f"Словарь сохранён в {OUTPUT_JSON}")
    print(f"Всего кодов: {len(result_dict)}")
    for code, words in list(result_dict.items())[:5]:
        top5 = dict(list(words.items())[:5])
        print(f"{code}: {top5}")

if __name__ == "__main__":
    main()
