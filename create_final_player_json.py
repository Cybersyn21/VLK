#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание финального JSON для музыкального плеера с правильными ссылками
"""

import json
from pathlib import Path


def load_page_links():
    """Загружает спарсенные ссылки"""
    with open('page_links_parsed.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_volkov2_json(filepath):
    """Загружает JSON файл из VOLKOV2.0"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_link_for_title(title, cd_songs):
    """Находит ссылку для заданного названия песни"""
    # Прямое совпадение
    if title in cd_songs:
        return cd_songs[title]

    # Поиск по частичному совпадению (без учета регистра)
    title_lower = title.lower()
    for song_title, link in cd_songs.items():
        if song_title.lower() == title_lower:
            return link

    # Поиск по началу названия (для коротких названий в page_links)
    for song_title, link in cd_songs.items():
        # Если название из page_links - начало полного названия
        if title_lower.startswith(song_title.lower()):
            return link
        # Если полное название начинается с названия из page_links
        if song_title.lower().startswith(title_lower):
            return link

    return None


def process_volkov2_cd(cd_num, page_links_data):
    """Обрабатывает один CD из VOLKOV2.0"""
    cd_key = f"CD{cd_num}"
    cd_dir = Path(f"VOLKOV2.0/{cd_key}")

    if not cd_dir.exists():
        print(f"⚠️  Папка {cd_dir} не найдена")
        return None

    cd_info = page_links_data.get(cd_key, {})
    cd_name = cd_info.get('name', f"CD{cd_num}")
    cd_songs = cd_info.get('songs', {})

    songs = []
    json_files = sorted(cd_dir.glob('*.json'))

    for json_file in json_files:
        try:
            data = load_volkov2_json(json_file)
            title = data.get('title', '')
            text = data.get('text', [])

            # Находим ссылку для этой песни
            link = find_link_for_title(title, cd_songs)
            if not link:
                print(f"⚠️  Ссылка не найдена для: {title}")
                link = f"https://v-volkov.ru/{json_file.stem}/"

            # Формируем объект песни
            # Извлекаем название альбома из cd_name
            album_title = cd_name.split(': ')[1].strip('"')

            song = {
                "title": title,
                "link": link,
                "track": {
                    "name": title,
                    "patch": f"/{album_title}/{title}.mp3"
                },
                "text": text
            }
            songs.append(song)

        except Exception as e:
            print(f"Ошибка при обработке {json_file}: {e}")

    return {
        "name": cd_name.split(': ')[1].strip('"'),
        "songs": songs
    }


def main():
    # Загружаем ссылки
    page_links = load_page_links()

    # Создаем структуру для плеера
    player_data = {
        "authorName": "Владимир Волков",
        "avatar": "volkov-avatar.jpg",
        "bio": [
            "Владимир Волков (1953-2017) - российский бард, поэт и композитор.",
            "Автор более 500 песен, охватывающих темы веры, любви к Родине и человеческой души."
        ],
        "bioAvatar": "img/volkov-bio.jpg",
        "albums": [],
        "stihi": [],
        "donationText": "Поддержите проект памяти Владимира Волкова",
        "donationLinks": [
            {
                "text": "Помочь проекту",
                "link": "https://v-volkov.ru/donate/"
            }
        ],
        "socialLinks": [
            {
                "text": "Официальный сайт",
                "link": "https://v-volkov.ru/"
            }
        ]
    }

    # Обрабатываем CD1-CD5
    for cd_num in [1, 2, 3, 4, 5]:
        print(f"\n📀 Обработка CD{cd_num}...")
        album = process_volkov2_cd(cd_num, page_links)
        if album:
            player_data["albums"].append(album)
            # Добавляем песни в общий список
            for song in album["songs"]:
                player_data["stihi"].append(song)
            print(f"✅ CD{cd_num}: {len(album['songs'])} песен")

    # Сохраняем результат
    output_file = 'volkov_player_with_links.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(player_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Финальный JSON создан: {output_file}")
    print(f"📊 Всего альбомов: {len(player_data['albums'])}")
    print(f"📊 Всего песен: {len(player_data['stihi'])}")


if __name__ == '__main__':
    main()
