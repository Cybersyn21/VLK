#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

def generate_ssilki_files():
    """Generate ssilki files for all albums based on JSON data"""

    album_names = {
        1: "Моя песня – на светлую чашу весов",
        2: "В той области небес",
        3: "Горит свеча",
        4: "Наша жизнь – слишком тонкая нить",
        5: "Не испачкавшись во лжи"
    }

    base_dir = Path('/home/user/VLK/STIHI_VOLKOV')
    output_dir = Path('/home/user/VLK/V-VOLKOV')

    for album_num in range(1, 6):
        album_dir = base_dir / f"CD{album_num}"

        # Get all JSON files in the album directory
        json_files = sorted(album_dir.glob("*.json"))

        # Parse track numbers and load data
        tracks = []
        for json_file in json_files:
            # Extract track number from filename (e.g., "01_dva_puti.json" -> 1)
            filename = json_file.name
            track_num_str = filename.split('_')[0]

            try:
                track_num = int(track_num_str)
            except ValueError:
                continue

            # Load JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tracks.append({
                'number': track_num,
                'title': data['title'],
                'link': data['link']
            })

        # Sort by track number
        tracks.sort(key=lambda x: x['number'])

        # Generate ssilki file
        output_file = output_dir / f"CD {album_num}" / f"ssilki0{album_num}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            album_name = album_names[album_num]
            f.write(f"Ссылки на аудиофайлы {['первого', 'второго', 'третьего', 'четвертого', 'пятого'][album_num-1]} альбома «{album_name}»\n\n")

            for track in tracks:
                f.write(f"{track['number']:02d}. {track['title']} — {track['link']}\n")

            f.write("\n")

        print(f"Created: CD {album_num}/ssilki0{album_num}.txt ({len(tracks)} tracks)")

if __name__ == '__main__':
    generate_ssilki_files()
    print("\nDone!")
