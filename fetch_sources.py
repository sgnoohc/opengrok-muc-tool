#!/usr/bin/env python3

import os
import sys
import re
import tarfile
import tempfile
import urllib.request
import subprocess

def safe_folder_name(name):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', name)

def download_and_extract_tarball(name, version, url, target_dir):
    folder = os.path.join(target_dir, f"{name}-{version}")
    if os.path.exists(folder):
        print(f"[SKIP] {folder} already exists")
        return

    try:
        print(f"Downloading tarball: {url}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as tmp:
            urllib.request.urlretrieve(url, tmp.name)
            os.makedirs(folder, exist_ok=True)
            print(f"Extracting to: {folder}")
            with tarfile.open(tmp.name, "r:gz") as tar:
                tar.extractall(folder)
        os.remove(tmp.name)
        print("Done.\n")
    except Exception as e:
        print(f"Failed to download or extract {url}: {e}")

def clone_git_commit(name, version, url, commit, target_dir):
    folder = os.path.join(target_dir, f"{name}-{version}")
    if os.path.exists(folder):
        print(f"[SKIP] {folder} already exists")
        return

    try:
        print(f"Cloning {url} at commit {commit} into {folder}")
        subprocess.run(["git", "clone", url, folder], check=True)
        subprocess.run(["git", "checkout", commit], cwd=folder, check=True)
        print("Done.\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone or checkout {url}@{commit}: {e}")


def process_line(line, target_dir="."):
    line = line.strip()
    if not line or "->" not in line:
        return

    left, right = line.split("->", 1)
    name_version = left.strip()
    name, version = name_version.split("@", 1)
    name = name.strip()
    version = version.strip()
    right = right.strip()

    # Case 1: .tar.gz
    if right.endswith(".tar.gz"):
        download_and_extract_tarball(name, version, right, target_dir)

    # Case 2: git repo with commit
    elif right.endswith(".git") or " at commit " in right:
        m = re.match(r'(https://github\.com/\S+\.git)\s+at\s+commit\s+([0-9a-f]{7,40})', right)
        if m:
            url, commit = m.groups()
            clone_git_commit(name, version, url, commit, target_dir)
        else:
            print(f"Could not parse git+commit from: {right}")
    else:
        print(f"Unrecognized source format: {right}")

def main():
    if len(sys.argv) != 2:
        print("Usage: ./fetch_sources.py <packages_to_download.txt>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r") as f:
        for line in f:
            process_line(line)

if __name__ == "__main__":
    main()

