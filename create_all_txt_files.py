#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path

def create_txt_from_json(json_file):
    """Create TXT file from JSON file"""

    # Read JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    title = data['title']
    text_lines = data['text']

    # Create TXT filename (same as JSON but with .txt extension)
    txt_file = json_file.with_suffix('.txt')

    # Build TXT content
    txt_content = f"{title}\n\n"

    # Add text lines
    for line in text_lines:
        txt_content += line + "\n"

    # Add empty line before JSON
    txt_content += "\n\n"

    # Add JSON at the end
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    txt_content += json_str

    # Write TXT file
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(txt_content)

    return txt_file

def main():
    volkov_dir = Path('/home/user/VLK/VOLKOV2.0')

    total_created = 0
    total_exists = 0

    for album_num in range(1, 6):
        cd_dir = volkov_dir / f"CD{album_num}"
        if not cd_dir.exists():
            print(f"WARNING: Directory {cd_dir} not found")
            continue

        json_files = sorted(cd_dir.glob("*.json"))
        print(f"\nProcessing CD{album_num}: {len(json_files)} JSON files")

        for json_file in json_files:
            txt_file = json_file.with_suffix('.txt')

            if txt_file.exists():
                total_exists += 1
                print(f"  EXISTS: {txt_file.name}")
            else:
                created = create_txt_from_json(json_file)
                total_created += 1
                print(f"  CREATED: {created.name}")

    print(f"\n{'='*60}")
    print(f"Total TXT files created:  {total_created}")
    print(f"Total TXT files existed:  {total_exists}")
    print(f"Total TXT files now:      {total_created + total_exists}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
