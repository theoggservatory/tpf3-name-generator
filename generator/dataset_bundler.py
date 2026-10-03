# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Oggservatory

import os
import json
import zipfile
from collections import defaultdict
from typing import Dict, Any, List

def build_bundled_world_dataset(
    cities_zip_path: str,
    country_info_path: str,
    output_path: str,
    deep_country_dumps: Dict[str, str] = None,
    default_limit: int = 500
) -> Dict[str, Any]:
    """
    Builds a single, clean, self-contained JSON dataset of the entire world
    from GeoNames under CC BY 4.0.
    """
    print("  [Bundler] Reading country metadata...")
    countries_meta = {}
    with open(country_info_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) > 4:
                iso2 = parts[0]
                countries_meta[iso2] = {
                    "name": parts[4],
                    "continent": parts[8] if len(parts) > 8 else "OTHER"
                }

    print("  [Bundler] Parsing worldwide populated places...")
    by_country = defaultdict(list)
    with zipfile.ZipFile(cities_zip_path, "r") as z:
        with z.open("cities5000.txt") as f:
            for line in f:
                parts = line.decode("utf-8", errors="replace").strip().split("\t")
                if len(parts) > 14:
                    cc = parts[8]
                    name = parts[1].strip()
                    pop = int(parts[14]) if parts[14].isdigit() else 0
                    fclass = parts[6]
                    if fclass == "P" and name:
                        by_country[cc].append((name, pop))

    bundled_data = {
        "_attribution": "Contains information from GeoNames (https://www.geonames.org), licensed under CC BY 4.0.",
        "_license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "countries": {}
    }

    # Process each country
    for cc, meta in countries_meta.items():
        cities = by_country.get(cc, [])
        cities.sort(key=lambda x: x[1], reverse=True)

        seen = set()
        clean_names = []
        for n, _ in cities:
            norm = n.lower()
            if norm not in seen and len(n) >= 2:
                seen.add(norm)
                clean_names.append(n)
            if len(clean_names) >= default_limit:
                break

        # Only include countries with at least 10 towns
        if len(clean_names) >= 10:
            bundled_data["countries"][cc] = {
                "name": meta["name"],
                "continent": meta["continent"],
                "towns": clean_names
            }

    # Incorporate deep country dumps if provided (e.g. for Finland 2000 towns)
    if deep_country_dumps:
        for cc, dump_path in deep_country_dumps.items():
            if os.path.exists(dump_path) and cc in bundled_data["countries"]:
                print(f"  [Bundler] Incorporating deep dump for {cc}...")
                with zipfile.ZipFile(dump_path, "r") as z:
                    txt_name = f"{cc}.txt"
                    if txt_name in z.namelist():
                        deep_seen = set()
                        deep_names = []
                        with z.open(txt_name) as f:
                            for line in f:
                                parts = line.decode("utf-8", errors="replace").strip().split("\t")
                                if len(parts) > 14 and parts[6] == "P" and parts[8] == cc:
                                    n = parts[1].strip()
                                    norm = n.lower()
                                    if norm not in deep_seen and len(n) >= 2 and not n[0].isdigit():
                                        deep_seen.add(norm)
                                        deep_names.append(n)
                                        if len(deep_names) >= 2000:
                                            break
                        if deep_names:
                            bundled_data["countries"][cc]["towns"] = deep_names
                            print(f"  [Bundler] Deep-loaded {len(deep_names)} places for {cc}.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(bundled_data, f, ensure_ascii=False, indent=2)

    sz_kb = os.path.getsize(output_path) / 1024
    print(f"  [Bundler] Wrote {len(bundled_data['countries'])} countries ({sz_kb:.1f} KB) to {output_path}")
    return bundled_data
