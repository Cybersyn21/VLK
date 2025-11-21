#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path

def parse_ssilki_file(filepath):
    """Parse ssilki file and extract clean track data"""
    tracks = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove [cite_start] and [cite: N] markers
    content = re.sub(r'\[cite_start\]', '', content)
    content = re.sub(r'\[cite:\s*\d+\]', '', content)

    # Pattern: ** NN. Title ** — `URL`
    pattern = r'\*\*\s*(\d+)\.\s*([^*]+?)\s*\*\*\s*[—-]\s*`([^`]+)`'

    for match in re.finditer(pattern, content):
        track_num = int(match.group(1))
        title = match.group(2).strip()
        url = match.group(3).strip()
        tracks.append({'num': track_num, 'title': title, 'url': url})

    return sorted(tracks, key=lambda x: x['num'])

def main():
    album_names = {
        1: "Моя песня – на светлую чашу весов",
        2: "В той области небес",
        3: "Горит свеча",
        4: "Наша жизнь – слишком тонкая нить",
        5: "Не испачкавшись во лжи"
    }

    album_ordinals = {
        1: "первого",
        2: "второго",
        3: "третьего",
        4: "четвертого",
        5: "пятого"
    }

    ssilki_dir = Path('/home/user/VLK/VOLKOV2.0_temp')
    output_dir = Path('/home/user/VLK/VOLKOV2.0')

    for i in range(1, 6):
        ssilki_file = ssilki_dir / f'ssilki0{i}.txt'
        tracks = parse_ssilki_file(ssilki_file)

        output_file = output_dir / f'ssilki0{i}.txt'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Ссылки на аудиофайлы {album_ordinals[i]} альбома «{album_names[i]}»\n\n")

            for track in tracks:
                f.write(f"{track['num']:02d}. {track['title']} — {track['url']}\n")

            f.write("\n")

        print(f"Created: ssilki0{i}.txt ({len(tracks)} tracks)")

    print("\nDone! All ssilki files created in uniform format.")

if __name__ == '__main__':
    main()
