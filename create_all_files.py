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


def parse_html_with_stanzas(html_content):
    """Parse HTML and properly detect stanzas"""
    poems = []

    # Find all anchors
    anchor_pattern = r'name="(D(\d)_(\d+))"'
    anchors = list(re.finditer(anchor_pattern, html_content))

    print(f"Found {len(anchors)} anchor matches")

    seen_anchors = set()

    for i, anchor_match in enumerate(anchors):
        anchor_name = anchor_match.group(1)
        album = int(anchor_match.group(2))
        track = int(anchor_match.group(3))

        if anchor_name in seen_anchors:
            continue
        seen_anchors.add(anchor_name)

        print(f"Processing {anchor_name}...")

        # Find all occurrences
        all_matches = [m for m in anchors if m.group(1) == anchor_name]

        title = None
        content_start_pos = None

        for match in all_matches:
            section_start = match.start()
            section_end = section_start + 500

            section = html_content[section_start:section_end]

            title_pattern = rf'name="{anchor_name}">([^<]+)</a>'
            title_match = re.search(title_pattern, section)

            if title_match:
                potential_title = title_match.group(1).strip()
                potential_title = re.sub(r'\[Д\d+_\d+:\d+\]', '', potential_title).strip()
                potential_title = potential_title.strip('! \t')

                if potential_title and '<' not in potential_title:
                    title = potential_title
                    marker_pattern = rf'</center><a name="{anchor_name}"><br>'
                    marker_match = re.search(marker_pattern, section)
                    if marker_match:
                        content_start_pos = section_start + marker_match.end()

        if not title:
            print(f"  No valid title found for {anchor_name}")
            continue

        print(f"  Title: {title}")

        if not content_start_pos:
            last_match = all_matches[-1]
            content_start_pos = last_match.end() + 200

        # Find end position
        next_anchor_pos = len(html_content)
        for next_match in anchors:
            if next_match.group(1) != anchor_name and next_match.start() > content_start_pos:
                next_anchor_pos = next_match.start()
                break

        # Extract content
        content_section = html_content[content_start_pos:next_anchor_pos]

        hr_pos = content_section.find('<hr')
        if hr_pos > 0:
            content = content_section[:hr_pos]
        else:
            content = content_section

        # Process content with proper stanza detection
        # Mark <dir> sections as separate stanzas
        content = re.sub(r'<dir[^>]*>', '§§§DIR_START§§§', content, flags=re.IGNORECASE)
        content = re.sub(r'</dir>', '§§§DIR_END§§§', content, flags=re.IGNORECASE)

        # Mark double <br> as stanza breaks
        # Pattern: <br> followed by whitespace/newline and another <br>
        # Replace with newline + marker + newline
        content = re.sub(r'<br\s*/?>\s*\n\s*<br\s*/?>', '\n§§§STANZA§§§\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<br\s*/?>\s*<br\s*/?>', '\n§§§STANZA§§§\n', content, flags=re.IGNORECASE)

        # Single <br> to newline
        content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)

        # Remove table tags and their attributes explicitly (may span multiple lines)
        content = re.sub(r'<table[^>]*>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'</table>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<tr[^>]*>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'</tr>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<td[^>]*>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'</td>', '', content, flags=re.IGNORECASE)

        # Remove all other HTML tags (may span multiple lines)
        content = re.sub(r'<[^>]+>', '', content, flags=re.DOTALL)

        # Clean up any remaining HTML attribute fragments (leftover from incomplete tag removal)
        content = re.sub(r'\w+padding="[^"]*"', '', content)
        content = re.sub(r'\w+spacing="[^"]*"', '', content)
        content = re.sub(r'[a-z]+="[^"]*"\s*>', '', content)
        # Remove standalone > or " > that might be left from table tags
        content = re.sub(r'^\s*["\']?\s*>\s*$', '', content, flags=re.MULTILINE)

        # Split into lines and clean
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # Handle DIR markers - add empty line before and after
            if '§§§DIR_START§§§' in line:
                if cleaned_lines and cleaned_lines[-1] != "":
                    cleaned_lines.append("")
                continue
            elif '§§§DIR_END§§§' in line:
                if cleaned_lines and cleaned_lines[-1] != "":
                    cleaned_lines.append("")
                continue
            # Handle stanza break marker
            elif '§§§STANZA§§§' in line:
                if cleaned_lines and cleaned_lines[-1] != "":
                    cleaned_lines.append("")
                continue

            # Skip empty lines
            if not line:
                continue

            # Remove markers and dedications
            line = re.sub(r'\[Д\d+_\d+:\d+\]', '', line)
            line = re.sub(r'\(Посвящается[^)]+\)', '', line)
            line = line.strip()

            if line and line != title:
                cleaned_lines.append(line)

        # Remove trailing empty lines
        while cleaned_lines and cleaned_lines[-1] == "":
            cleaned_lines.pop()

        # Remove leading empty lines
        while cleaned_lines and cleaned_lines[0] == "":
            cleaned_lines.pop(0)

        if cleaned_lines:
            poems.append({
                'album': album,
                'track': track,
                'title': title,
                'text': cleaned_lines
            })

    return poems


def create_txt_and_json_files(poems):
    """Create both .txt and .json files for all poems"""
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

        # Create filenames
        translit = transliterate_title(title)
        if not translit:
            translit = f"track{track}"

        json_filename = f"{track:02d}_{translit}.json"
        txt_filename = f"{album:02d}_{track}_{title}.txt"

        # Output directory
        output_dir = base_dir / f"CD{album}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write JSON file
        json_path = output_dir / json_filename
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_obj, f, ensure_ascii=False, indent=2)

        # Write TXT file (text + JSON at the end)
        txt_path = output_dir / txt_filename
        with open(txt_path, 'w', encoding='utf-8') as f:
            # Write title
            f.write(f"{title}\n\n")

            # Write text with proper line breaks
            for line in text:
                f.write(f"{line}\n")

            # Add separator
            f.write("\n\n")

            # Write JSON
            f.write(json.dumps(json_obj, ensure_ascii=False, indent=2))
            f.write("\n\n")

        print(f"Created: CD{album}/{txt_filename}")


def main():
    html_path = '/home/user/VLK/V-VOLKOV/#U0412#U043b#U0430#U0434#U0438#U043c#U0438#U0440 #U0412#U043e#U043b#U043a#U043e#U0432 #U2013 #U0422#U0435#U043a#U0441#U0442#U044b #U043f#U0435#U0441#U0435#U043d.html'

    print("Reading HTML file...")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Parsing poems with proper stanza detection...")
    poems = parse_html_with_stanzas(html_content)
    print(f"Found {len(poems)} poems\n")

    print("Creating TXT and JSON files...")
    create_txt_and_json_files(poems)

    print(f"\nDone! Created {len(poems)} files.")


if __name__ == '__main__':
    main()
