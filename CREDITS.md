# Credits & Attribution

This project adheres to open source best practices, data licensing compliance, and transparent asset provenance.

---

## 1. Geographic Data Sources

### GeoNames
* **Source:** [GeoNames Geographic Database](https://www.geonames.org/)
* **License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
* **Attribution Notice:** Contains information from GeoNames (https://www.geonames.org), made available under the Creative Commons Attribution 4.0 International License.
* **Authenticity Statement:** All geographic place names, coordinates, and hierarchies in this project originate from authoritative official GeoNames records. None of the geographic data is synthetic or AI-generated.
* **Transformations & Modifications:**
  - Filtered exclusively for populated places (`feature_class = 'P'`, including national capitals, regional administrative centers, cities, towns, villages, and parishes).
  - Cleaned and normalized strings (stripped extraneous administrative markers, coordinates, and obsolete parentheticals).
  - Ranked hierarchically by administrative tier and census population data.
  - Serialized into UTF-8 Lua tables formatted specifically for the Transport Fever 3 engine.

---

## 2. Artificial Intelligence & Tooling Disclosure

* **Mod Cover Art (`generator/0.png`):** Generated using the Google Gemini image generation model via [Google Antigravity](https://deepmind.google/technologies/gemini/).
* **Development Assistance:** Code architecture, reverse engineering of engine scripts, and documentation were created with pair-programming assistance from Google Antigravity.

---

## 3. Game & Engine Trademarks

* **Transport Fever 3** is a video game developed by [Urban Games](https://www.urbangames.com/) and published by [Good Shepherd Entertainment](https://goodshepherd.games/).
* This repository is an independent, community-developed open-source tool and mod. It is not affiliated with, endorsed by, or sponsored by Urban Games or Good Shepherd Entertainment.
