# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Oggservatory

import os
import sys
import json
import argparse
import zipfile
import shutil
from typing import Dict, Any, List

from generator.lua_writer import write_tf3_towns_lua, write_tf3_names_lua, write_tf3_names_script, write_tf3_mod_manifest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_PATH = os.path.join(BASE_DIR, "data", "places", "world.json")
DEFAULT_MOD_ID = "ogg_world_names_1"
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "mods", DEFAULT_MOD_ID)

# Map continent codes to friendly names
CONTINENT_NAMES = {
    "EU": "Europe",
    "NA": "North America",
    "SA": "South America",
    "AS": "Asia",
    "AF": "Africa",
    "OC": "Oceania"
}

def find_steam_mod_targets(custom_common: str = None, custom_userdata: str = None) -> List[str]:
    """
    Dynamically discovers Transport Fever 3 mod directories without hardcoding personal account IDs.
    Supports user overrides via CLI flags or environment variables.
    """
    targets = []
    
    # 1. Steam common install directory
    common_path = custom_common or os.environ.get("TF3_COMMON_MODS")
    if not common_path:
        default_candidates = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Transport Fever 3\mods",
            r"C:\Program Files\Steam\steamapps\common\Transport Fever 3\mods",
        ]
        for c in default_candidates:
            if os.path.exists(c):
                common_path = c
                break
    if common_path and os.path.exists(common_path) and common_path not in targets:
        targets.append(common_path)

    # 2. Steam userdata local mod directories (App ID 3493540)
    if custom_userdata or os.environ.get("TF3_USERDATA_MODS"):
        u_path = custom_userdata or os.environ.get("TF3_USERDATA_MODS")
        if os.path.exists(u_path) and u_path not in targets:
            targets.append(u_path)
    else:
        userdata_bases = [
            r"C:\Program Files (x86)\Steam\userdata",
            r"C:\Program Files\Steam\userdata",
        ]
        for s_base in userdata_bases:
            if os.path.isdir(s_base):
                for uid in os.listdir(s_base):
                    mod_dir = os.path.join(s_base, uid, "3493540", "local", "mods")
                    if os.path.exists(mod_dir) and mod_dir not in targets:
                        targets.append(mod_dir)

    return targets

def load_world_data(data_path: str = DEFAULT_DATA_PATH) -> Dict[str, Any]:
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Bundled dataset not found at: {data_path}")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_pipeline(
    data_path: str = DEFAULT_DATA_PATH,
    countries_filter: List[str] = None,
    continent_filter: str = None,
    limit_override: int = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    create_zip: bool = False,
    install_to_game: bool = False,
    steam_common: str = None,
    steam_userdata: str = None,
    author: str = "Nahkki",
    mod_name: str = None
) -> None:
    print("=" * 65)
    print(" Transport Fever 3 - Open Data Name Pack Generator")
    print(" Native TF3 Engine Format | Powered by GeoNames (CC BY 4.0)")
    print("=" * 65)

    dataset = load_world_data(data_path)
    all_countries = dataset.get("countries", {})

    # Select target countries
    selected = {}
    if countries_filter:
        requested = [c.strip().upper() for c in countries_filter]
        for cc, data in all_countries.items():
            if cc in requested or data["name"].upper() in requested:
                selected[cc] = data
        if not selected:
            print(f"[Error] No countries matched filter: {countries_filter}")
            sys.exit(1)
    elif continent_filter:
        cont_upper = continent_filter.upper()
        for cc, data in all_countries.items():
            if data.get("continent", "").upper() == cont_upper:
                selected[cc] = data
        if not selected:
            print(f"[Error] No countries matched continent: {continent_filter}")
            sys.exit(1)
    else:
        # Default: All countries in dataset
        selected = all_countries

    # Default mod title based on selection
    if not mod_name:
        if continent_filter:
            cont_name = CONTINENT_NAMES.get(continent_filter.upper(), continent_filter.upper())
            mod_name = f"Authentic {cont_name} Town Names"
        elif countries_filter and len(countries_filter) == 1:
            country_name = list(selected.values())[0]["name"]
            mod_name = f"Authentic {country_name} Town Names"
        elif countries_filter and len(countries_filter) <= 4:
            names = [selected[c]["name"] for c in selected][:3]
            mod_name = f"Authentic {', '.join(names)} Town Names"
        else:
            mod_name = "Global Town Names (All Countries)"

    mod_id = os.path.basename(output_dir.rstrip("/\\"))
    print(f"\nMod ID: {mod_id}")
    print(f"Mod Name: {mod_name}")
    print(f"Selected Countries: {len(selected)}")
    print(f"Output Destination: {output_dir}\n")

    os.makedirs(output_dir, exist_ok=True)

    total_towns = 0

    # Sort countries alphabetically by English name
    sorted_countries = sorted(selected.items(), key=lambda x: x[1]["name"])

    for cc, info in sorted_countries:
        c_name = info["name"]
        towns = info.get("towns", [])
        if limit_override:
            towns = towns[:limit_override]

        region_slug = c_name.lower().replace(" ", "_").replace("-", "_")
        region_slug = "".join(ch for ch in region_slug if ch.isalnum() or ch == "_")

        # In TF3: content/names/<region_slug>/<region_slug>.names.lua
        # and content/names/<region_slug>/en/towns.lua
        country_names_dir = os.path.join(output_dir, "content", "names", region_slug)
        names_lua_path = os.path.join(country_names_dir, f"{region_slug}.names.lua")
        towns_lua_path = os.path.join(country_names_dir, "en", "towns.lua")

        write_tf3_names_lua(names_lua_path, display_name=c_name, path_slug=region_slug, mod_id=mod_id)
        write_tf3_towns_lua(towns_lua_path, towns)
        total_towns += len(towns)

    # Write content/names/names.script.lua so the engine finds ogg_world_names_1::/names/names.script
    names_script_path = os.path.join(output_dir, "content", "names", "names.script.lua")
    write_tf3_names_script(names_script_path)

    # Write TF3 root manifests: mod.json and _metadata/modinfo.json
    write_tf3_mod_manifest(output_dir, mod_id=mod_id, mod_name=mod_name, author=author)
    print(f"[Manifest] Generated TF3 mod.json and _metadata/modinfo.json for {len(sorted_countries)} countries.")

    # Packaging
    if create_zip:
        dist_dir = os.path.join(BASE_DIR, "dist")
        os.makedirs(dist_dir, exist_ok=True)
        zip_path = os.path.join(dist_dir, f"{mod_id}.zip")
        print(f"\n[Packaging] Creating distribution zip: {zip_path}...")
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(output_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, os.path.dirname(output_dir))
                    zf.write(full_path, rel_path)
        print(f"  -> Successfully generated {zip_path}")

    # Optional Auto-Install (Installs to both Common and Userdata mods directories)
    if install_to_game:
        install_targets = find_steam_mod_targets(steam_common, steam_userdata)
        installed_locations = []
        for base_path in install_targets:
            if os.path.exists(base_path):
                dest = os.path.join(base_path, mod_id)
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(output_dir, dest)
                installed_locations.append(dest)
        
        if installed_locations:
            print(f"\n[Installed] Successfully installed mod to:")
            for loc in installed_locations:
                print(f"  {loc}")
        else:
            print("\n[Warning] Could not find Steam game or userdata mods folder.")

    print("\n" + "=" * 65)
    print(" BUILD SUMMARY")
    print("=" * 65)
    print(f" - Countries packaged: {len(sorted_countries)}")
    print(f" - Total towns generated: {total_towns:,}")
    print(f"\nMod ready at: {output_dir}")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Generate native Transport Fever 3 name mods from bundled open data.")
    parser.add_argument("--data", default=DEFAULT_DATA_PATH, help="Path to world.json dataset.")
    parser.add_argument("--country", default=None, help="Comma-separated country codes or names (e.g. FI,EE,SE).")
    parser.add_argument("--continent", default=None, help="Filter by continent (e.g. EU, NA, AS, SA, AF, OC).")
    parser.add_argument("--limit", type=int, default=None, help="Max towns per country.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Destination folder for the mod.")
    parser.add_argument("--zip", action="store_true", help="Create a .zip archive in dist/.")
    parser.add_argument("--install", action="store_true", help="Automatically install into Transport Fever 3 mods directories.")
    parser.add_argument("--steam-common", default=None, help="Custom Steam common mods directory path.")
    parser.add_argument("--steam-userdata", default=None, help="Custom Steam userdata mods directory path.")
    parser.add_argument("--mod-name", default=None, help="Custom mod display name in-game.")
    parser.add_argument("--author", default="Nahkki", help="Author name for mod metadata.")

    args = parser.parse_args()

    countries_filter = [c.strip() for c in args.country.split(",")] if args.country else None

    run_pipeline(
        data_path=args.data,
        countries_filter=countries_filter,
        continent_filter=args.continent,
        limit_override=args.limit,
        output_dir=args.output_dir,
        create_zip=args.zip,
        install_to_game=args.install,
        steam_common=args.steam_common,
        steam_userdata=args.steam_userdata,
        author=args.author,
        mod_name=args.mod_name
    )

if __name__ == "__main__":
    main()
