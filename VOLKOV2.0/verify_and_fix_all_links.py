#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from pathlib import Path

def parse_ssilki_file(filepath):
    """Parse ssilki file and extract track number -> URL mapping"""
    links = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern: NN. Title — URL
    pattern = r'(\d+)\.\s+([^—]+?)\s+—\s+(https?://[^\s]+)'

    for match in re.finditer(pattern, content):
        track_num = int(match.group(1))
        title = match.group(2).strip()
        url = match.group(3).strip()
        links[track_num] = {'title': title, 'url': url}

    return links

def verify_and_fix_json_files():
    """Verify and fix all JSON files"""
    volkov_dir = Path('/home/user/VLK/VOLKOV2.0')

    # Parse all ssilki files
    all_links = {}
    for i in range(1, 6):
        ssilki_file = volkov_dir / f'ssilki0{i}.txt'
        links = parse_ssilki_file(ssilki_file)
        all_links[i] = links
        print(f"Parsed {len(links)} links from ssilki0{i}.txt")

    total_checked = 0
    total_fixed = 0
    total_errors = 0

    for album_num in range(1, 6):
        cd_dir = volkov_dir / f"CD{album_num}"
        if not cd_dir.exists():
            print(f"WARNING: Directory {cd_dir} not found")
            continue

        json_files = sorted(cd_dir.glob("*.json"))
        print(f"\nChecking CD{album_num}: {len(json_files)} JSON files")

        for json_file in json_files:
            total_checked += 1

            # Extract track number from filename
            track_num_str = json_file.name.split('_')[0]
            try:
                track_num = int(track_num_str)
            except ValueError:
                print(f"  WARNING: Can't parse track number from {json_file.name}")
                total_errors += 1
                continue

            # Load JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Get expected link from ssilki
            if track_num in all_links[album_num]:
                expected_link = all_links[album_num][track_num]['url']
                current_link = data.get('link', '')

                if current_link != expected_link:
                    print(f"  FIXING: CD{album_num} track {track_num:02d}")
                    print(f"    Current:  {current_link}")
                    print(f"    Expected: {expected_link}")

                    data['link'] = expected_link
                    total_fixed += 1

                    # Save fixed JSON
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    # Update corresponding TXT file
                    txt_pattern = f"{track_num:02d}_{album_num}_*.txt"
                    txt_files = list(cd_dir.glob(txt_pattern))

                    for txt_file in txt_files:
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            txt_content = f.read()

                        # Find JSON part and replace
                        json_start = txt_content.rfind('{')
                        if json_start != -1:
                            txt_before_json = txt_content[:json_start]
                            new_txt_content = txt_before_json + json.dumps(data, ensure_ascii=False, indent=2)

                            with open(txt_file, 'w', encoding='utf-8') as f:
                                f.write(new_txt_content)

                            print(f"    Updated TXT: {txt_file.name}")
                else:
                    print(f"  ✓ CD{album_num} track {track_num:02d}: {data['title']}")
            else:
                print(f"  WARNING: No link found in ssilki for CD{album_num} track {track_num}")
                total_errors += 1

    print(f"\n{'='*60}")
    print(f"Total files checked: {total_checked}")
    print(f"Total files fixed:   {total_fixed}")
    print(f"Total errors:        {total_errors}")
    print(f"{'='*60}")

    return total_fixed

if __name__ == '__main__':
    print("Verifying and fixing all JSON/TXT files...\n")
    fixed = verify_and_fix_json_files()

    if fixed > 0:
        print(f"\n✓ Fixed {fixed} files!")
    else:
        print("\n✓ All files are already correct!")
