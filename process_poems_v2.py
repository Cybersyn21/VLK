#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import os
from pathlib import Path

def transliterate_title(title):
    """Transliterate Russian title to Latin for URL"""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        ' ': '_', ',': '', '.': '', '!': '', '?': '', '–': '', '—': '',
        ':': '', ';': '', '"': '', "'": '', '…': '', '«': '', '»': ''
    }

    title_lower = title.lower()
    result = []
    for char in title_lower:
        if char in translit_map:
            result.append(translit_map[char])
        elif char.isalnum():
            result.append(char)

    transliterated = ''.join(result)
    transliterated = re.sub(r'_+', '_', transliterated)
    transliterated = transliterated.strip('_')

    return transliterated


def get_audio_link(album, track, title):
    """Generate audio link for poem"""
    ssilki_path = f'/home/user/VLK/V-VOLKOV/CD {album}/ssilki0{album}.txt'

    if os.path.exists(ssilki_path):
        with open(ssilki_path, 'r', encoding='utf-8') as f:
            for line in f:
                if f'{track:02d}.' in line or f' {track}.' in line:
                    url_match = re.search(r'https://[^\s]+\.mp3', line)
                    if url_match:
                        return url_match.group(0)

    translit = transliterate_title(title)
    return f"https://v-volkov.ru/audio/cd{album}/{album}{track:02d}_vlk_{translit}.mp3"


def parse_html_simple(html_content):
    """Simple and robust HTML parser"""
    poems = []

    # Find all anchors with name="D#_##"
    anchor_pattern = r'name="(D(\d)_(\d+))"'
    anchors = list(re.finditer(anchor_pattern, html_content))

    print(f"Found {len(anchors)} anchor matches")

    # Skip duplicates - only process unique anchors
    seen_anchors = set()

    for i, anchor_match in enumerate(anchors):
        anchor_name = anchor_match.group(1)
        album = int(anchor_match.group(2))
        track = int(anchor_match.group(3))

        # Skip if we've already processed this anchor
        if anchor_name in seen_anchors:
            continue
        seen_anchors.add(anchor_name)

        print(f"Processing {anchor_name}...")

        # Find ALL occurrences of this anchor
        all_matches = [m for m in anchors if m.group(1) == anchor_name]

        # The LAST occurrence is usually before the actual text
        # Find the last one that has the title
        title = None
        content_start_pos = None

        for match in all_matches:
            section_start = match.start()
            section_end = section_start + 500  # Look ahead 500 chars

            section = html_content[section_start:section_end]

            # Try to find title
            title_pattern = rf'name="{anchor_name}">([^<]+)</a>'
            title_match = re.search(title_pattern, section)

            if title_match:
                potential_title = title_match.group(1).strip()
                potential_title = re.sub(r'\[Д\d+_\d+:\d+\]', '', potential_title).strip()
                potential_title = potential_title.strip('! \t')

                if potential_title and '<' not in potential_title:
                    title = potential_title
                    # Look for text after </center><a name="..."><br>
                    # This is usually where the poem starts
                    marker_pattern = rf'</center><a name="{anchor_name}"><br>'
                    marker_match = re.search(marker_pattern, section)
                    if marker_match:
                        content_start_pos = section_start + marker_match.end()

        if not title:
            print(f"  No valid title found for {anchor_name}")
            continue

        print(f"  Title: {title}")

        if not content_start_pos:
            # Fallback: find last anchor and start after it
            last_match = all_matches[-1]
            content_start_pos = last_match.end() + 200  # Skip some tags

        # Find end position (before next poem's first anchor)
        # Look for the next poem anchor (different name)
        next_anchor_pos = len(html_content)
        for next_match in anchors:
            if next_match.group(1) != anchor_name and next_match.start() > content_start_pos:
                next_anchor_pos = next_match.start()
                break

        # Extract content
        content_section = html_content[content_start_pos:next_anchor_pos]

        # Stop at <hr> tag if present
        hr_pos = content_section.find('<hr')
        if hr_pos > 0:
            content = content_section[:hr_pos]
        else:
            content = content_section

        # Process content
        # Replace <br><br> or <br> <br> with stanza marker
        content = re.sub(r'<br\s*/?>\s*<br\s*/?>', '\n\n§§§STANZA§§§\n\n', content, flags=re.IGNORECASE)
        # Replace single <br> with newline
        content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
        # Remove all HTML tags
        content = re.sub(r'<[^>]+>', '', content)

        # Split into lines and clean
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # Skip empty lines and stanza markers for now
            if not line or '§§§STANZA§§§' in line:
                if '§§§STANZA§§§' in line and cleaned_lines and cleaned_lines[-1] != "":
                    cleaned_lines.append("")
                continue

            # Remove markers
            line = re.sub(r'\[Д\d+_\d+:\d+\]', '', line)
            # Remove dedications
            line = re.sub(r'\(Посвящается[^)]+\)', '', line)
            line = line.strip()

            # Skip if line is same as title or empty
            if not line or line == title:
                continue

            cleaned_lines.append(line)

        # Remove trailing empty lines
        while cleaned_lines and cleaned_lines[-1] == "":
            cleaned_lines.pop()

        if cleaned_lines:
            poems.append({
                'album': album,
                'track': track,
                'title': title,
                'text': cleaned_lines
            })

    return poems


def create_json_files(poems):
    """Create JSON files for all poems"""
    base_dir = Path('/home/user/VLK/STIHI_VOLKOV')

    for poem in poems:
        album = poem['album']
        track = poem['track']
        title = poem['title']
        text = poem['text']

        # Get audio link
        audio_link = get_audio_link(album, track, title)

        # Create JSON object
        json_obj = {
            'title': title,
            'link': audio_link,
            'text': text
        }

        # Create filename
        translit = transliterate_title(title)
        if not translit:
            translit = f"track{track}"
        filename = f"{track:02d}_{translit}.json"

        # Determine output directory
        output_dir = base_dir / f"CD{album}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write JSON file
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_obj, f, ensure_ascii=False, indent=2)

        print(f"Created: CD{album}/{filename} - {title}")


def main():
    html_path = '/home/user/VLK/V-VOLKOV/#U0412#U043b#U0430#U0434#U0438#U043c#U0438#U0440 #U0412#U043e#U043b#U043a#U043e#U0432 #U2013 #U0422#U0435#U043a#U0441#U0442#U044b #U043f#U0435#U0441#U0435#U043d.html'

    print("Reading HTML file...")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Parsing poems...")
    poems = parse_html_simple(html_content)
    print(f"Found {len(poems)} poems\n")

    print("Creating JSON files...")
    create_json_files(poems)

    print(f"\nDone! Created {len(poems)} JSON files.")


if __name__ == '__main__':
    main()
