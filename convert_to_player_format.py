#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для создания единого JSON файла для музыкального плеера
Конвертирует файлы из VOLKOV2.0 в формат для Vue.js 3 плеера
"""

import json
from pathlib import Path
from transliterate import translit

def transliterate_title(title):
    """Транслитерация названия для URL"""
    try:
        # Используем ГОСТ 7.79-2000
        result = translit(title, 'ru', reversed=True)
        # Заменяем пробелы и спецсимволы на дефисы
        result = result.lower()
        result = result.replace(' ', '-')
        result = result.replace(',', '')
        result = result.replace('.', '')
        result = result.replace('!', '')
        result = result.replace('?', '')
        result = result.replace(':', '')
        result = result.replace(';', '')
        result = result.replace('–', '-')
        result = result.replace('—', '-')
        result = result.replace('«', '')
        result = result.replace('»', '')
        result = result.replace('(', '')
        result = result.replace(')', '')
        # Убираем множественные дефисы
        while '--' in result:
            result = result.replace('--', '-')
        # Убираем дефисы в начале и конце
        result = result.strip('-')
        return result
    except:
        # Если транслитерация не работает, используем простую замену
        result = title.lower()
        replacements = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            ' ': '-', ',': '', '.': '', '!': '', '?': '', ':': '', ';': '',
            '–': '-', '—': '-', '«': '', '»': '', '(': '', ')': ''
        }
        for ru, en in replacements.items():
            result = result.replace(ru, en)
        while '--' in result:
            result = result.replace('--', '-')
        return result.strip('-')

def convert_volkov_to_player_format(base_url="https://v-volkov.ru"):
    """
    Конвертирует файлы VOLKOV2.0 в формат для плеера
    """
    volkov_dir = Path('/home/user/VLK/VOLKOV2.0')

    # Названия альбомов
    album_names = {
        1: "Моя песня – на светлую чашу весов",
        2: "В той области небес",
        3: "Горит свеча",
        4: "Наша жизнь – слишком тонкая нить",
        5: "Не испачкавшись во лжи"
    }

    all_tracks = []

    # Обрабатываем каждый альбом
    for cd_num in range(1, 6):
        cd_dir = volkov_dir / f"CD{cd_num}"
        album_name = album_names[cd_num]

        if not cd_dir.exists():
            print(f"WARNING: Directory {cd_dir} not found")
            continue

        json_files = sorted(cd_dir.glob("*.json"))
        print(f"\nProcessing CD{cd_num}: {album_name}")
        print(f"Found {len(json_files)} tracks")

        for json_file in json_files:
            # Читаем JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data['title']
            link = data.get('link', '')
            text = data['text']

            # Извлекаем название файла из ссылки
            if link:
                # Например: https://v-volkov.ru/audio/cd1/101_vlk_dva_puti.mp3
                mp3_filename = link.split('/')[-1]
            else:
                # Если нет ссылки, генерируем название
                mp3_filename = f"{json_file.stem}.mp3"

            # Создаем транслитерированное название для URL
            url_title = transliterate_title(title)

            # Создаем запись в формате плеера
            track_entry = {
                "title": title,
                "link": f"{base_url}/{url_title}",
                "track": {
                    "name": title,
                    "patch": f"/{album_name}/{mp3_filename}"
                },
                "text": text
            }

            all_tracks.append(track_entry)
            print(f"  ✓ {title}")

    return all_tracks

def save_player_json(tracks, output_file):
    """Сохраняет JSON для плеера"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tracks, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Saved {len(tracks)} tracks to {output_file}")
    print(f"{'='*60}")

def main():
    print("Converting VOLKOV2.0 to music player format...\n")

    # Конвертируем
    tracks = convert_volkov_to_player_format()

    # Сохраняем
    output_file = Path('/home/user/VLK/volkov_player_data.json')
    save_player_json(tracks, output_file)

    # Также сохраняем в VOLKOV2.0
    output_file2 = Path('/home/user/VLK/VOLKOV2.0/player_data.json')
    save_player_json(tracks, output_file2)

    print("\n✓ Conversion complete!")
    print(f"\nTotal tracks: {len(tracks)}")
    print("\nNext steps:")
    print("1. Добавить 52 песни раннего творчества")
    print("2. Настроить пути к MP3 файлам")
    print("3. Проверить URL для страниц")

if __name__ == '__main__':
    main()
