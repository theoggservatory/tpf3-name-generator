# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Oggservatory

import os
import sys
import urllib.request
import urllib.error

USER_AGENT = "TransportFever3NameGen/1.0 (+https://github.com/theoggservatory/tpf3-name-generator; open source data pipeline)"

def get_cache_dir() -> str:
    """Returns the path to the local cache directory."""
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache", "geonames")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def download_file_with_cache(url: str, filename: str, force_refresh: bool = False) -> str:
    """
    Downloads a static file from a data source if not already cached.
    Ensures considerate network usage by never re-downloading existing files.
    """
    cache_path = os.path.join(get_cache_dir(), filename)

    if os.path.exists(cache_path) and not force_refresh:
        file_size_mb = os.path.getsize(cache_path) / (1024 * 1024)
        print(f"  [Cache hit] Using cached {filename} ({file_size_mb:.2f} MB)")
        return cache_path

    print(f"  [Downloading] {url} -> {filename}...")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "identity",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            total_size = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 64 * 1024
            
            with open(cache_path, "wb") as out_file:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = (downloaded / total_size) * 100
                        sys.stdout.write(f"\r  Downloading: {pct:.1f}% ({downloaded / (1024 * 1024):.2f} MB / {total_size / (1024 * 1024):.2f} MB)")
                        sys.stdout.flush()
            print("\n  Download complete.")
            return cache_path

    except urllib.error.HTTPError as e:
        print(f"\n  [HTTP Error] Failed to download {url}: {e.code} {e.reason}")
        if os.path.exists(cache_path):
            os.remove(cache_path)
        raise
    except Exception as e:
        print(f"\n  [Error] Failed to download {url}: {e}")
        if os.path.exists(cache_path):
            os.remove(cache_path)
        raise
