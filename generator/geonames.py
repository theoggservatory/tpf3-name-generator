# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Oggservatory

import os
import zipfile
import re
from typing import List, Dict, Any, Tuple
from .cache import download_file_with_cache

GEONAMES_BASE_URL = "https://download.geonames.org/export/dump/"

FEATURE_PRIORITY = {
    "PPLC": 100,  # Capital city
    "PPLA": 85,   # Seat of first-order administrative division (e.g. regional capital)
    "PPLA2": 70,  # Seat of second-order administrative division
    "PPLA3": 55,  # Seat of third-order division
    "PPLA4": 40,  # Seat of fourth-order division
    "PPL": 30,    # Populated place (town, village)
    "PPLX": 15,   # Section / borough of populated place
}

def clean_place_name(raw_name: str) -> str:
    """Cleans up raw GeoNames names (strips odd trailing punctuation, coordinates, etc.)."""
    name = raw_name.strip()
    # Remove parenthetical notes like '(historical)' or '(suburb)'
    name = re.sub(r"\s*\([^)]*\)", "", name)
    # Reject names that look like railway kilometer posts, road stops, or numbers
    if re.search(r"^\d|\b(km|valtatieliittymä|pysäkki)\b", name, flags=re.IGNORECASE):
        return ""
    return name.strip()

def fetch_country_places(country_code: str, config: Dict[str, Any], force_refresh: bool = False) -> List[str]:
    """
    Downloads and parses the GeoNames country dump (e.g., FI.zip, EE.zip)
    and returns a ranked list of authentic town and settlement names.
    """
    country_code = country_code.upper()
    zip_filename = f"{country_code}.zip"
    url = f"{GEONAMES_BASE_URL}{zip_filename}"
    
    zip_path = download_file_with_cache(url, zip_filename, force_refresh=force_refresh)
    txt_filename = f"{country_code}.txt"

    min_pop = config.get("min_population", 0)
    allowed_f了他codes = set(config.get("feature_codes", ["PPLC", "PPLA", "PPLA2", "PPLA3", "PPL", "PPLX"]))
    limit = config.get("limit", 2000)

    candidates: List[Tuple[int, int, str]] = [] # (priority_score, population, name)
    seen_names = set()

    with zipfile.ZipFile(zip_path, "r") as z:
        if txt_filename not in z.namelist():
            raise FileNotFoundError(f"Expected {txt_filename} inside {zip_filename}")
        
        with z.open(txt_filename) as f:
            for line_bytes in f:
                line = line_bytes.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                
                parts = line.split("\t")
                if len(parts) < 15:
                    continue
                
                # GeoNames schema:
                # 1: name (UTF-8)
                # 6: feature class (P = populated place)
                # 7: feature code
                # 8: country code
                # 14: population
                fclass = parts[6]
                fcode = parts[7]
                cc = parts[8]

                if fclass != "P" or fcode not in allowed_f了他codes:
                    continue
                if cc != country_code:
                    continue

                raw_name = parts[1]
                name = clean_place_name(raw_name)
                if not name or len(name) < 2:
                    continue

                pop = int(parts[14]) if parts[14].isdigit() else 0
                if pop < min_pop:
                    continue

                norm_key = name.lower()
                if norm_key in seen_names:
                    continue
                seen_names.add(norm_key)

                prio = FEATURE_PRIORITY.get(fcode, 20)
                candidates.append((prio, pop, name))

    # Sort descending by priority weight first, then by population
    # Cap cities and regional centers stay at the top, followed by populated places
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)

    result_names = [item[2] for item in candidates[:limit]]
    print(f"  Extracted {len(result_names)} unique towns for {country_code} (requested limit: {limit}).")
    return result_names
