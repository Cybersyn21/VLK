#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавление CD9 (Раннее творчество) в JSON плеера
"""

import json
from pathlib import Path


def load_json(filepath):
    """Загружает JSON файл"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    # Загружаем существующий JSON плеера
    player_data = load_json('volkov_player_with_links.json')

    # Загружаем ссылки для CD9
    page_links = load_json('page_links_parsed.json')
    cd9_data = page_links.get('CD9', {})
    cd9_songs = cd9_data.get('songs', {})

    # Загружаем тексты из TEXT и TEXT_EXTRACTED
    text_dir = Path('TEXT')
    text_extracted_dir = Path('TEXT_EXTRACTED')
    cd9_stihi = []

    # Обрабатываем только 50 песен (51-52 не публикуем)
    song_count = 0
    for title, link in cd9_songs.items():
        if song_count >= 50:
            break

        # Сначала проверяем наличие .json файла в TEXT (верифицированные)
        possible_json_files = list(text_dir.glob(f"{title}.mp3.json"))

        if not possible_json_files:
            # Пытаемся найти по частичному совпадению
            possible_json_files = [f for f in text_dir.glob("*.mp3.json")
                                    if title.lower() in f.stem.replace('.mp3', '').lower()]

        text_content = []

        if possible_json_files:
            # Используем верифицированный .json файл
            try:
                json_file = possible_json_files[0]
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # Разбиваем на строки
                    text_content = [line for line in content.split('\n') if line.strip()]
                print(f"✅ {title}: используем верифицированный .json")
            except Exception as e:
                print(f"⚠️  Ошибка при чтении {possible_json_files[0]}: {e}")
        else:
            # Ищем извлеченный текст в TEXT_EXTRACTED
            possible_txt_files = list(text_extracted_dir.glob(f"*{title[:20]}*.txt"))

            if not possible_txt_files:
                # Поиск по более короткому началу
                for txt_file in text_extracted_dir.glob("*.txt"):
                    if txt_file.stem != 'index' and title.lower()[:15] in txt_file.stem.lower():
                        possible_txt_files = [txt_file]
                        break

            if possible_txt_files:
                try:
                    txt_file = possible_txt_files[0]
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Пропускаем первую строку (заголовок) и пустые строки
                        text_content = []
                        skip_first = True
                        for line in lines:
                            line = line.strip()
                            if skip_first and line:
                                skip_first = False
                                continue  # Пропускаем заголовок
                            if line or text_content:  # Добавляем пустые строки только после первой строки текста
                                text_content.append(line)
                    print(f"📝 {title}: используем извлеченный текст")
                except Exception as e:
                    print(f"⚠️  Ошибка при чтении {possible_txt_files[0]}: {e}")
            else:
                print(f"❌ Файл не найден для: {title}")

        # Формируем объект песни
        song = {
            "title": title,
            "link": link,
            "track": {
                "name": title,
                "patch": f"/Раннее творчество/{title}.mp3"
            },
            "text": text_content if text_content else [
                f"(Текст песни '{title}' будет добавлен позже)"
            ]
        }
        cd9_stihi.append(song)
        song_count += 1

    # Добавляем CD9 в альбомы
    cd9_album = {
        "name": "Раннее творчество",
        "songs": cd9_stihi
    }
    player_data["albums"].append(cd9_album)

    # Добавляем песни в общий список stihi
    player_data["stihi"].extend(cd9_stihi)

    # Сохраняем обновленный JSON
    output_file = 'volkov_player_complete.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(player_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Полный JSON создан: {output_file}")
    print(f"📊 Всего альбомов: {len(player_data['albums'])}")
    print(f"📊 Всего песен: {len(player_data['stihi'])}")
    print(f"📊 CD9 (Раннее творчество): {len(cd9_stihi)} песен")


if __name__ == '__main__':
    main()
