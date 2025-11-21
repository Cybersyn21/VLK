#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсинг файлов page_links и создание JSON для музыкального плеера
"""

import json
import re
from pathlib import Path


def parse_page_links(filepath):
    """Парсит файл page_links и возвращает словарь {название: ссылка}"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    songs = {}
    current_title = None
    cd_name = None

    for line in lines:
        line = line.strip()

        # Пропускаем пустые строки и комментарии
        if not line or line.startswith('не публикуем'):
            break  # Прекращаем парсинг если дошли до "не публикуем!!!"

        # Название альбома
        if line.startswith('CD'):
            cd_name = line
            continue

        # Проверяем, это название песни или ссылка
        if line.startswith('http'):
            if current_title:
                songs[current_title] = line
                current_title = None
        else:
            # Убираем номер в начале (формат: "01. Название" или "1. Название")
            match = re.match(r'^\d+\.\s*(.+)$', line)
            if match:
                current_title = match.group(1)

    return cd_name, songs


def main():
    html_dir = Path('HTML')

    # Файлы page_links для всех альбомов
    page_links_files = {
        'CD1': 'page_links_01_vlk_mp3tag.html',
        'CD2': 'page_links_02_vlk_mp3tag.html',
        'CD3': 'page_links_03_vlk_mp3tag.html',
        'CD4': 'page_links_04_vlk_mp3tag.html',
        'CD5': 'page_links_05_vlk_mp3tag.html',
        'CD9': 'page_links_rannee.html'
    }

    all_links = {}

    for cd, filename in page_links_files.items():
        filepath = html_dir / filename
        if filepath.exists():
            cd_name, songs = parse_page_links(filepath)
            all_links[cd] = {
                'name': cd_name,
                'songs': songs
            }
            print(f"\n{cd_name}")
            print(f"Найдено песен: {len(songs)}")
            for title, link in list(songs.items())[:3]:
                print(f"  - {title}: {link}")
            if len(songs) > 3:
                print(f"  ... и еще {len(songs) - 3} песен")
        else:
            print(f"Файл не найден: {filepath}")

    # Сохраняем в JSON
    output_file = 'page_links_parsed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_links, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Результат сохранен в {output_file}")

    # Статистика
    total_songs = sum(len(cd_data['songs']) for cd_data in all_links.values())
    print(f"\n📊 Всего песен: {total_songs}")
    for cd, cd_data in all_links.items():
        print(f"   {cd}: {len(cd_data['songs'])} песен")


if __name__ == '__main__':
    main()
