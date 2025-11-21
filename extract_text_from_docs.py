#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Извлечение текстов из .doc и .docx файлов из папки TEXT
"""

import os
import json
from pathlib import Path

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    print("WARNING: python-docx not installed. Install with: pip install python-docx")

try:
    import subprocess
    HAS_ANTIWORD = True
except:
    HAS_ANTIWORD = False

def extract_from_docx(filepath):
    """Извлечение текста из .docx файла"""
    if not HAS_DOCX:
        return None

    try:
        doc = Document(filepath)
        lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                lines.append(text)
            else:
                lines.append("")  # Пустая строка для разделения строф
        return lines
    except Exception as e:
        print(f"ERROR extracting {filepath}: {e}")
        return None

def extract_from_doc(filepath):
    """Извлечение текста из .doc файла через antiword"""
    try:
        result = subprocess.run(
            ['antiword', str(filepath)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.returncode == 0:
            text = result.stdout
            # Разбиваем на строки и очищаем
            lines = []
            for line in text.split('\n'):
                stripped = line.strip()
                if stripped:
                    lines.append(stripped)
                elif lines and lines[-1] != "":  # Добавляем пустую строку только если предыдущая не пустая
                    lines.append("")
            return lines
        else:
            print(f"ERROR: antiword failed for {filepath}")
            return None
    except FileNotFoundError:
        print("ERROR: antiword not found. Install with: apt-get install antiword")
        return None
    except Exception as e:
        print(f"ERROR extracting {filepath}: {e}")
        return None

def get_title_from_filename(filename):
    """Извлекает название песни из имени файла"""
    # Убираем нумерацию и транслитерацию
    # Формат: 000Название песни_номер_transliteratsiya_192.doc
    # или: ААА-Название песни_номер_transliteratsiya_192.doc

    name = filename.replace('.doc', '').replace('.docx', '')

    # Убираем префиксы 000 или ААА-
    if name.startswith('000'):
        name = name[3:]
    elif name.startswith('ААА-'):
        name = name[4:]

    # Находим последнее подчеркивание и берем все до него
    parts = name.rsplit('_', 3)  # Разбиваем с конца на 3 части
    if len(parts) > 1:
        title = parts[0]
    else:
        title = name

    return title

def main():
    text_dir = Path('/home/user/VLK/TEXT')
    output_dir = Path('/home/user/VLK/TEXT_EXTRACTED')
    output_dir.mkdir(exist_ok=True)

    # Находим все .doc и .docx файлы
    doc_files = sorted(list(text_dir.glob('*.doc')) + list(text_dir.glob('*.docx')))

    print(f"Found {len(doc_files)} documents\n")

    extracted = []

    for doc_file in doc_files:
        if doc_file.name.endswith('.docx'):
            print(f"Processing: {doc_file.name} (.docx)")
            lines = extract_from_docx(doc_file)
        else:
            print(f"Processing: {doc_file.name} (.doc)")
            lines = extract_from_doc(doc_file)

        if lines:
            title = get_title_from_filename(doc_file.name)

            # Проверяем, есть ли .mp3.json файл с таким же названием
            json_file = text_dir / f"{title}.mp3.json"
            has_json = json_file.exists()

            # Сохраняем извлеченный текст
            output_file = output_dir / f"{title}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(title + '\n\n')
                for line in lines:
                    f.write(line + '\n')

            extracted.append({
                'title': title,
                'source_file': doc_file.name,
                'output_file': output_file.name,
                'has_json': has_json,
                'lines_count': len(lines)
            })

            print(f"  ✓ Extracted: {title}")
            print(f"    Lines: {len(lines)}, Has JSON: {has_json}")
        else:
            print(f"  ✗ Failed to extract")

        print()

    # Сохраняем индекс
    index_file = output_dir / 'index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Extracted {len(extracted)} documents")
    print(f"Saved to: {output_dir}")
    print(f"Index: {index_file}")
    print(f"{'='*60}")

    # Статистика
    with_json = sum(1 for item in extracted if item['has_json'])
    without_json = len(extracted) - with_json

    print(f"\nStatistics:")
    print(f"  With .mp3.json files: {with_json}")
    print(f"  Without .mp3.json:    {without_json}")
    print(f"  Total:                {len(extracted)}")

if __name__ == '__main__':
    main()
