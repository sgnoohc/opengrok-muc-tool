#!/usr/bin/env python3

import sys

OUTPUT_FILE = "merge_to_download.txt"

def parse_package_name(line):
    """Extract package name before the @ sign."""
    if '->' not in line:
        return None
    lhs = line.split('->')[0].strip()
    if '@' in lhs:
        return lhs.split('@')[0].strip()
    return None

def load_file_to_map(filename):
    """Returns dict: package -> full line"""
    package_map = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or '->' not in line:
                continue
            pkg = parse_package_name(line)
            if pkg:
                package_map[pkg] = line
    return package_map

def main():
    if len(sys.argv) != 3:
        print("Usage: ./merge_package_sources.py file1.txt file2.txt")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]

    map1 = load_file_to_map(file1)
    map2 = load_file_to_map(file2)

    # Merge: start with file2, overwrite with file1 (file1 has priority)
    merged = dict(map2)
    merged.update(map1)

    with open(OUTPUT_FILE, 'w') as out:
        for line in sorted(merged.values()):
            out.write(line + '\n')

    print(f"Merged output written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

