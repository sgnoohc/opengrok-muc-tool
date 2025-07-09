#!/usr/bin/env python3

import subprocess
import sys
import re
import os

def get_deps(spec):
    try:
        output = subprocess.check_output(['spack', 'spec', spec], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running spack spec: {e}", file=sys.stderr)
        sys.exit(1)

    deps = []
    for line in output.splitlines():
        match = re.search(r'\^([^\s@]+)@([^\s%]+)', line)
        if match:
            name, version = match.groups()
            deps.append((name, version))
    return deps

def get_source_url(name, version):
    try:
        output = subprocess.check_output(['spack', 'info', f'{name}@{version}'], text=True)
    except subprocess.CalledProcessError:
        return None

    in_safe = False
    for line in output.splitlines():
        if line.strip().startswith("Safe versions:"):
            in_safe = True
            continue
        if in_safe and line.strip() == "":
            break

        if in_safe and re.search(rf'^{re.escape(version)}\s+', line.strip()):
            tar_match = re.search(r'(https?://\S+\.tar\.gz)', line)
            if tar_match:
                return tar_match.group(1)

            git_match = re.search(r'\[git\]\s+(https?://\S+\.git)', line)
            commit_match = re.search(r'\b([0-9a-f]{7,40})\b', line)
            if git_match and commit_match:
                return f"{git_match.group(1)} at commit {commit_match.group(1)}"

    return None

def read_allowed_url_patterns(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"Error reading allowed URL pattern file: {e}", file=sys.stderr)
        sys.exit(1)

def read_package_whitelist(filename):
    try:
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip() and not line.startswith('#'))
    except Exception as e:
        print(f"Error reading whitelist: {e}", file=sys.stderr)
        sys.exit(1)

def write_parsed_deps(deps, filename):
    try:
        with open(filename, 'w') as f:
            for name, version in deps:
                f.write(f"{name} {version}\n")
    except Exception as e:
        print(f"Error writing parsed package list: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 4:
        print("Usage: ./get_sources.py <spack-spec> <whitelist-file> <url-filter-file>")
        sys.exit(1)

    spec = sys.argv[1]
    whitelist_file = sys.argv[2]
    url_filter_file = sys.argv[3]

    allowed_patterns = read_allowed_url_patterns(url_filter_file)
    tracked = read_package_whitelist(whitelist_file)
    deps = get_deps(spec)

    suffix = spec.replace('/', '_').replace('@', '_').replace('%', '_')
    parsed_output_file = f"packages_parsed.{suffix}.txt"
    download_output_file = f"packages_to_download.{suffix}.txt"

    write_parsed_deps(deps, parsed_output_file)

    try:
        out_file = open(download_output_file, 'w')
    except Exception as e:
        print(f"Error opening {download_output_file}: {e}", file=sys.stderr)
        sys.exit(1)

    for name, version in deps:
        if name.startswith("py-"):
            continue
        if name not in tracked:
            continue

        url = get_source_url(name, version)
        if url and any(pat in url for pat in allowed_patterns):
            line = f"{name}@{version} -> {url}"
            print(line)
            out_file.write(line + "\n")

    out_file.close()


if __name__ == "__main__":
    main()

