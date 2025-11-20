#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import os
from html.parser import HTMLParser
from pathlib import Path

class VolkovPoemsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.poems = []
        self.current_poem = None
        self.in_poem = False
        self.poem_text = []
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        # Detect poem start by anchor tag with name attribute
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'name' and value.startswith('D'):
                    # Extract album and track number (e.g., D1_01, D2_10)
                    match = re.match(r'D(\d)_(\d+)', value)
                    if match:
                        album = int(match.group(1))
                        track = int(match.group(2))
                        if self.current_poem:
                            # Save previous poem
                            self.poems.append(self.current_poem)
                        self.current_poem = {
                            'album': album,
                            'track': track,
                            'anchor': value,
                            'title': '',
                            'text': []
                        }
                        self.in_poem = True
                        self.poem_text = []

    def handle_data(self, data):
        if self.in_poem and data.strip():
            # Collect text data
            self.poem_text.append(data.strip())

    def handle_endtag(self, tag):
        self.current_tag = None

    def get_poems(self):
        if self.current_poem:
            self.poems.append(self.current_poem)
        return self.poems


def clean_poem_text(text):
    """Clean poem text by removing technical markers and dedications"""
    # Remove markers like [Д1_02:146]
    text = re.sub(r'\[Д\d+_\d+:\d+\]', '', text)
    # Remove dedications like (Посвящается ...)
    text = re.sub(r'\(Посвящается[^)]+\)', '', text)
    # Remove extra whitespace
    text = text.strip()
    return text


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

    # Remove multiple underscores
    transliterated = ''.join(result)
    transliterated = re.sub(r'_+', '_', transliterated)
    transliterated = transliterated.strip('_')

    return transliterated


def parse_html_file(html_path):
    """Parse HTML file and extract all poems"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    poems = []

    # Find all poem sections
    # Look for pattern: <a name="D#_##">Title</a> where title is inside the anchor tag
    pattern = r'<a name="(D\d_\d+)">([^<]+)</a>(.*?)(?=<a name="D\d_\d+">|<hr|$)'
    matches = re.finditer(pattern, html_content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        anchor = match.group(1)
        title = match.group(2).strip()
        content = match.group(3)

        # Extract album and track
        anchor_match = re.match(r'D(\d)_(\d+)', anchor)
        if not anchor_match:
            continue

        album = int(anchor_match.group(1))
        track = int(anchor_match.group(2))

        # Clean title
        # Remove markers like [Д#_##:###]
        title = re.sub(r'\[Д\d+_\d+:\d+\]', '', title).strip()
        # Remove trailing spaces and special chars
        title = title.strip('! ')

        # Skip if title is empty or looks like HTML
        if not title or '<' in title:
            continue

        # Extract poem text
        # Replace double <br> with special marker for stanza breaks
        poem_text = re.sub(r'<br\s*/?>\s*<br\s*/?>', '\n\n§§§STANZA§§§\n\n', content)
        # Replace single <br> with newline
        poem_text = re.sub(r'<br\s*/?>', '\n', poem_text)
        # Remove all HTML tags
        poem_text = re.sub(r'<[^>]+>', '', poem_text)

        # Split into lines
        lines = [line.strip() for line in poem_text.split('\n')]

        # Remove dedications and markers, preserve stanza breaks
        cleaned_lines = []
        for line in lines:
            # Check if this is a stanza break marker
            if '§§§STANZA§§§' in line:
                # Add empty line if previous line wasn't empty
                if cleaned_lines and cleaned_lines[-1] != "":
                    cleaned_lines.append("")
                continue

            if not line:
                # Empty line - preserve it
                if cleaned_lines and cleaned_lines[-1] != "":
                    cleaned_lines.append("")
                continue

            # Remove markers
            line = re.sub(r'\[Д\d+_\d+:\d+\]', '', line)
            # Remove dedications
            line = re.sub(r'\(Посвящается[^)]+\)', '', line)
            line = line.strip()
            if line and line != title:  # Don't include title in text
                cleaned_lines.append(line)

        if cleaned_lines:
            poems.append({
                'album': album,
                'track': track,
                'anchor': anchor,
                'title': title,
                'text': cleaned_lines
            })

    return poems


def get_audio_link(album, track, title):
    """Generate audio link for poem"""
    # Read links from ssilki files
    ssilki_path = f'/home/user/VLK/V-VOLKOV/CD {album}/ssilki0{album}.txt'

    if os.path.exists(ssilki_path):
        with open(ssilki_path, 'r', encoding='utf-8') as f:
            for line in f:
                if f'{track:02d}.' in line or f'{track}.' in line:
                    # Extract URL from line
                    url_match = re.search(r'https://[^\s]+\.mp3', line)
                    if url_match:
                        return url_match.group(0)

    # Fallback: generate URL based on transliterated title
    translit = transliterate_title(title)
    return f"https://v-volkov.ru/audio/cd{album}/{album}{track:02d}_vlk_{translit}.mp3"


def process_poem_text(text_lines):
    """Process poem text - clean up trailing empty lines"""
    if not text_lines:
        return []

    # Remove trailing empty lines
    while text_lines and text_lines[-1] == "":
        text_lines.pop()

    # Remove leading empty lines
    while text_lines and text_lines[0] == "":
        text_lines.pop(0)

    return text_lines


def create_json_files(poems):
    """Create JSON files for all poems"""
    base_dir = Path('/home/user/VLK/STIHI_VOLKOV')

    for poem in poems:
        album = poem['album']
        track = poem['track']
        title = poem['title']
        text = poem['text']

        # Process text to add stanza breaks
        processed_text = process_poem_text(text)

        # Get audio link
        audio_link = get_audio_link(album, track, title)

        # Create JSON object
        json_obj = {
            'title': title,
            'link': audio_link,
            'text': processed_text
        }

        # Create filename
        translit = transliterate_title(title)
        filename = f"{track:02d}_{translit}.json"

        # Determine output directory
        output_dir = base_dir / f"CD{album}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write JSON file
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_obj, f, ensure_ascii=False, indent=2)

        print(f"Created: {output_path}")


def main():
    html_path = '/home/user/VLK/V-VOLKOV/#U0412#U043b#U0430#U0434#U0438#U043c#U0438#U0440 #U0412#U043e#U043b#U043a#U043e#U0432 #U2013 #U0422#U0435#U043a#U0441#U0442#U044b #U043f#U0435#U0441#U0435#U043d.html'

    print("Parsing HTML file...")
    poems = parse_html_file(html_path)
    print(f"Found {len(poems)} poems")

    print("Creating JSON files...")
    create_json_files(poems)

    print("Done!")


if __name__ == '__main__':
    main()
