#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Создание полного JSON файла для музыкального плеера Владимира Волкова
По аналогии с форматом content.json для Станислава Андрейчика
"""

import json
from pathlib import Path

def transliterate_simple(text):
    """Простая транслитерация для URL"""
    result = text.lower()
    replacements = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        ' ': '_', ',': '', '.': '', '!': '', '?': '', ':': '', ';': '',
        '–': '-', '—': '-', '«': '', '»': '', '(': '', ')': '', ' - ': '_'
    }
    for ru, en in replacements.items():
        result = result.replace(ru, en)
    # Убираем множественные подчеркивания
    while '__' in result:
        result = result.replace('__', '_')
    return result.strip('_')

def create_player_json():
    """Создает полный JSON для плеера"""

    volkov_dir = Path('/home/user/VLK/VOLKOV2.0')

    # Информация об альбомах
    albums_info = {
        1: {"name": "Моя песня – на светлую чашу весов", "year": ""},
        2: {"name": "В той области небес", "year": ""},
        3: {"name": "Горит свеча", "year": ""},
        4: {"name": "Наша жизнь – слишком тонкая нить", "year": ""},
        5: {"name": "Не испачкавшись во лжи", "year": ""}
    }

    # Корневая структура JSON
    content = {
        "authorName": "Владимир Волков",
        "avatar": "volkov-avatar.jpg",
        "bio": [],
        "bioAvatar": "img/volkov-bio.jpg",
        "albums": [],
        "stihi": [],
        "donationText": "Поддержите проект памяти Владимира Волкова",
        "donationLinks": [
            {"title": "Сайт", "link": "https://v-volkov.ru"},
            {"title": "Скачать альбомы", "link": "https://v-volkov.ru/audio/"},
            {"title": "О проекте", "link": "https://v-volkov.ru/about"}
        ],
        "socialLinks": [
            {"title": "VK", "link": "https://vk.com/v_volkov"},
            {"title": "YouTube", "link": "https://youtube.com/@vladimirvolk"},
        ]
    }

    # Создаем массив альбомов
    for cd_num in range(1, 6):
        cd_dir = volkov_dir / f"CD{cd_num}"
        album_name = albums_info[cd_num]['name']

        if not cd_dir.exists():
            continue

        json_files = sorted(cd_dir.glob("*.json"))

        # Создаем треки для альбома
        tracks = []
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data['title']
            link = data.get('link', '')

            # Извлекаем название MP3 файла
            if link:
                mp3_filename = link.split('/')[-1]
            else:
                track_num = int(json_file.name.split('_')[0])
                mp3_filename = f"{cd_num}0{track_num}_vlk_{json_file.stem}.mp3"

            # URL для страницы песни
            url_title = transliterate_simple(title)

            tracks.append({
                "name": title,
                "patch": f"/{album_name}/{mp3_filename}",
                "link": f"https://v-volkov.ru/{url_title}"
            })

        # Добавляем альбом
        content["albums"].append({
            "name": album_name,
            "avatar": f"img/album{cd_num}.jpg",
            "tracks": tracks
        })

    # Создаем массив всех стихов/песен
    for cd_num in range(1, 6):
        cd_dir = volkov_dir / f"CD{cd_num}"
        album_name = albums_info[cd_num]['name']

        if not cd_dir.exists():
            continue

        json_files = sorted(cd_dir.glob("*.json"))

        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data['title']
            link = data.get('link', '')
            text = data['text']

            # Извлекаем название MP3 файла
            if link:
                mp3_filename = link.split('/')[-1]
            else:
                track_num = int(json_file.name.split('_')[0])
                mp3_filename = f"{cd_num}0{track_num}_vlk_{json_file.stem}.mp3"

            # URL для страницы песни
            url_title = transliterate_simple(title)

            # Добавляем в массив стихов
            content["stihi"].append({
                "title": title,
                "link": f"https://v-volkov.ru/{url_title}",
                "track": {
                    "name": title,
                    "patch": f"/{album_name}/{mp3_filename}"
                },
                "text": text
            })

    return content

def main():
    print("Creating Volkov music player JSON...\n")

    # Создаем JSON
    content = create_player_json()

    # Сохраняем
    output_file = Path('/home/user/VLK/volkov_content.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    # Также сохраняем в VOLKOV2.0
    output_file2 = Path('/home/user/VLK/VOLKOV2.0/content.json')
    with open(output_file2, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    print(f"{'='*60}")
    print(f"✓ Created {output_file}")
    print(f"✓ Created {output_file2}")
    print(f"{'='*60}")
    print(f"\nStatistics:")
    print(f"  Albums: {len(content['albums'])}")
    print(f"  Total tracks: {len(content['stihi'])}")
    print(f"\nAlbums:")
    for i, album in enumerate(content['albums'], 1):
        print(f"  CD{i}: {album['name']} - {len(album['tracks'])} tracks")

    print("\n✓ Conversion complete!")
    print("\nNext steps:")
    print("1. Добавить информацию bio об авторе")
    print("2. Добавить 52 песни раннего творчества из папки TEXT")
    print("3. Настроить правильные пути к изображениям")
    print("4. Обновить ссылки на социальные сети")

if __name__ == '__main__':
    main()
