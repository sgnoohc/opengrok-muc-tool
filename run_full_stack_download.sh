#!/bin/bash

set -e

# Absolute path to the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TRACKED_STACK_FILE="$SCRIPT_DIR/tracked_stack.txt"
TRACKED_PKG_FILE="$SCRIPT_DIR/tracked_packages.txt"
URL_FILTER_FILE="$SCRIPT_DIR/url-filter.txt"
MERGED_OUTPUT="$SCRIPT_DIR/merge_to_download.txt"
DOWNLOAD_DIR="/opengrok/src"

# Ensure required files exist
for f in "$TRACKED_STACK_FILE" "$TRACKED_PKG_FILE" "$URL_FILTER_FILE"; do
    if [ ! -f "$f" ]; then
        echo "Missing required file: $f"
        exit 1
    fi
done

# Step 1: Run get_sources.py for each stack
while read -r stack; do
    [ -z "$stack" ] && continue
    echo "Generating source list for stack: $stack"
    python3 "$SCRIPT_DIR/get_sources.py" "$stack" "$TRACKED_PKG_FILE" "$URL_FILTER_FILE"
done < "$TRACKED_STACK_FILE"

# Step 2: Merge all `packages_to_download.*.txt` into a single file
DOWNLOAD_FILES=$(ls "$SCRIPT_DIR"/packages_to_download.*.txt 2>/dev/null)
if [ -z "$DOWNLOAD_FILES" ]; then
    echo "No packages_to_download.*.txt files found"
    exit 1
fi

echo "Merging download lists..."
first=1
while read -r stack; do
    [ -z "$stack" ] && continue
    if [ "$first" -eq 1 ]; then
        cp "$SCRIPT_DIR/packages_to_download.$stack.txt" "$SCRIPT_DIR/__merged_tmp.txt"
        first=0
    else
        python3 "$SCRIPT_DIR/merge_package_sources.py" "$SCRIPT_DIR/__merged_tmp.txt" "$SCRIPT_DIR/packages_to_download.$stack.txt"
        mv "$SCRIPT_DIR/merge_to_download.txt" "$SCRIPT_DIR/__merged_tmp.txt"
    fi
done < "$TRACKED_STACK_FILE"
mv "$SCRIPT_DIR/__merged_tmp.txt" "$MERGED_OUTPUT"
echo "Final merged download list written to: $MERGED_OUTPUT"

# Step 3: Download sources to ~/src
echo "Downloading sources into $DOWNLOAD_DIR"
mkdir -p "$DOWNLOAD_DIR"
cd $DOWNLOAD_DIR
python3 "$SCRIPT_DIR/fetch_sources.py" "$MERGED_OUTPUT"

echo "All done."
