# Transport Fever 3 - Open Data Name Pack Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

A lightweight, data-driven pipeline that generates authentic town and city name pools for **Transport Fever 3** using open geographic data.

Instead of subjective, hand-picked lists or micro-language debates, this project systematically compiles **200+ countries** directly from the official **GeoNames** database under [Creative Commons Attribution 4.0 (CC BY 4.0)](CREDITS.md).

---

## Features

* **Authentic Regional Variety:** From major capitals down to small historic church villages, parishes, and railway settlements (e.g. 2,000+ authentic Finnish and Estonian places).
* **100% Offline & Deterministic:** Bundles a clean, normalized extract of the world ([`data/places/world.json`](data/places/world.json) — under 800 KB total). Builds instantly without hitting any external APIs.
* **Respectful Open Data Citizen:** Zero live API hammering, zero authentication requirements.
* **Native Transport Fever 3 Mod:** Generates the exact native structure expected by the engine (`content/names/...`, `mod.json`, and `_metadata/modinfo.json`).

---

## Quickstart: Installing the Mod in Transport Fever 3

If you just want to play with the mod in your game:

1. Download or copy the pre-built mod folder:
   ```text
   mods/ogg_world_names_1/
   ```
2. Place it into your Transport Fever 3 `mods` directory:
   * **Windows (Default Steam location):**
     ```text
     C:\Program Files (x86)\Steam\steamapps\common\Transport Fever 3\mods\
     ```
     > **Note on Windows paths:** Unlike many games that store mods in `Documents`, Urban Games' engine loads local mods directly from the `mods/` directory inside the Steam installation folder or from Steam userdata (`userdata/<UserID>/3493540/local/mods/`).
3. Launch Transport Fever 3, start a new **Free Game**, open **Advanced Settings**, and select your desired country under **Town Names**!

> **Tip:** You can also auto-install directly with:
> ```bash
> python generate.py --continent EU --install
> ```

---

## Generator CLI (For Developers & Modders)

The Python generator requires **no third-party dependencies** (uses only standard library Python 3.10+):

### 1. Build All European Countries (Default 45 Nations)
```bash
python generate.py --continent EU --zip
```

### 2. Build a Dedicated Country Pack (e.g. Finland)
```bash
python generate.py --country FI --mod-name "Authentic Finnish Town Names" --zip
```

### 3. Build a Regional Multi-Country Pack (e.g. Northern Europe)
```bash
python generate.py --country FI,EE,SE,NO,DK --mod-name "Northern Europe Town Names" --zip
```

### 4. Build the Complete World (200 Countries)
```bash
python generate.py --zip
```

### Auto-Installation Flags
* `--install`: Automatically discovers and installs to your local Steam game and user mod folders.
* `--steam-common <path>`: (Optional) Specify a custom Steam common mods folder.
* `--steam-userdata <path>`: (Optional) Specify a custom Steam userdata mods folder.

All distribution archives are automatically generated into `dist/`.

---

## License & Attribution

This repository follows a dual-licensing structure to respect software code and geographic dataset rights:

* **Source Code:** Licensed under the [MIT License](LICENSE).
  ```
  SPDX-License-Identifier: MIT
  Copyright (c) 2026 Nahkki / The Oggservatory
  ```
* **Geographic Data:** Sourced from the [GeoNames Geographical Database](https://www.geonames.org/), licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
* **Full Attribution & AI Disclosure:** Detailed attribution, dataset transformation notes, and asset provenance are documented in [CREDITS.md](CREDITS.md).
