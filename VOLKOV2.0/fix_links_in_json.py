#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import shutil
from pathlib import Path

def parse_ssilki_file(filepath):
    """Parse ssilki file and extract track number -> URL mapping"""
    links = {}

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
        links[track_num] = {'title': title, 'url': url}

    return links

def main():
    # Parse all ssilki files
    ssilki_dir = Path('/home/user/VLK/VOLKOV2.0_temp')
    all_links = {}

    for i in range(1, 6):
        ssilki_file = ssilki_dir / f'ssilki0{i}.txt'
        links = parse_ssilki_file(ssilki_file)
        all_links[i] = links
        print(f"Parsed {len(links)} links from album {i}")

    # Copy STIHI_VOLKOV to VOLKOV2.0 and fix links
    source_dir = Path('/home/user/VLK/STIHI_VOLKOV')
    target_dir = Path('/home/user/VLK/VOLKOV2.0')

    # Clear target directory
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir()

    for i in range(1, 6):
        cd_source = source_dir / f"CD{i}"
        cd_target = target_dir / f"CD{i}"
        cd_target.mkdir()

        # Get all JSON files
        json_files = sorted(cd_source.glob("*.json"))

        for json_file in json_files:
            # Extract track number from filename
            track_num_str = json_file.name.split('_')[0]
            try:
                track_num = int(track_num_str)
            except ValueError:
                print(f"WARNING: Can't parse track number from {json_file.name}")
                continue

            # Load JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Replace link with correct one from ssilki
            if i in all_links and track_num in all_links[i]:
                correct_link = all_links[i][track_num]['url']
                data['link'] = correct_link
                print(f"Fixed: CD{i} track {track_num:02d} - {data['title']}")
            else:
                print(f"WARNING: No link found for CD{i} track {track_num}")

            # Save fixed JSON
            target_file = cd_target / json_file.name
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Copy TXT file as well
            txt_pattern = f"{track_num:02d}_{i}_*.txt"
            txt_files = list(cd_source.glob(txt_pattern))
            if txt_files:
                for txt_file in txt_files:
                    # Update JSON in TXT file as well
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        txt_content = f.read()

                    # Find JSON part and replace
                    json_start = txt_content.rfind('{')
                    if json_start != -1:
                        txt_before_json = txt_content[:json_start]
                        new_txt_content = txt_before_json + json.dumps(data, ensure_ascii=False, indent=2)

                        target_txt = cd_target / txt_file.name
                        with open(target_txt, 'w', encoding='utf-8') as f:
                            f.write(new_txt_content)

    print(f"\nDone! All files copied and links fixed.")

if __name__ == '__main__':
    main()
