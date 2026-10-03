# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Oggservatory

import os
import json
from typing import List, Dict, Any

def escape_lua_string(val: str) -> str:
    """Escapes quotes and backslashes for valid Lua string literals."""
    return val.replace("\\", "\\\\").replace('"', '\\"')

def write_tf3_towns_lua(filepath: str, names: List[str]) -> None:
    """Writes a native Transport Fever 3 towns.lua table (return { "City", ... })."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write("return {\n")
        for name in names:
            escaped = escape_lua_string(name)
            f.write(f'\t"{escaped}",\n')
        f.write("}\n")

def write_tf3_names_script(filepath: str) -> None:
    """
    Writes content/names/names.script.lua into the mod so that the game engine
    resolves ogg_world_names_1::/names/names.script@townsNameScriptFn without 'Resource not found' errors.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write('''local names = nil
local ok, res = pcall(require, "::/names/personnameutil.lua")
if ok and res then
	names = res
else
	local ok2, res2 = pcall(require, "personnameutil.lua")
	if ok2 and res2 then
		names = res2
	end
end

local getLangOrFallback = function(captureParams, params)
	if captureParams and captureParams.languages then
		return captureParams.languages[params.lang] or captureParams.languages["fallback"] or "en"
	end
	return "en"
end

function data()
return {
	personNameScriptFn = function(captureParams, params)
		local p = (captureParams and captureParams.path) or "unitedKingdom"
		if names and names[p] then
			local n = names[p][params.lang] or names[p].en
			if n then
				local firstNamesMale = n.firstNamesMale or { "John", "Alexander", "Daniel" }
				local firstNamesFemale = n.firstNamesFemale or { "Mary", "Emma", "Sarah" }
				local lastNames = n.lastNames or { "Smith", "Taylor", "Brown" }
				if (params.isMale) then
					return firstNamesMale[math.random(#firstNamesMale)] .. " " .. lastNames[math.random(#lastNames)]
				else
					return firstNamesFemale[math.random(#firstNamesFemale)] .. " " .. lastNames[math.random(#lastNames)]
				end
			end
		end
		if (params.isMale) then
			return "John Smith"
		else
			return "Mary Smith"
		end
	end,
	townsNameScriptFn = function(captureParams, params)
		local modPrefix = captureParams.modId and (captureParams.modId .. "::") or ""
		local lang = getLangOrFallback(captureParams, params)
		local towns = nil
		local ok, res = pcall(require, modPrefix .. "/names/" .. captureParams.path .. "/" .. lang .. "/towns.lua")
		if ok and res then
			towns = res
		else
			local ok2, res2 = pcall(require, "/names/" .. captureParams.path .. "/" .. lang .. "/towns.lua")
			if ok2 and res2 then
				towns = res2
			end
		end
		if not towns or #towns == 0 then
			return {}
		end
		if params.num < 0 then
			return towns
		end
		if params.num <= 1 or params.num > #towns then
			local res = {}
			for k = 1, params.num do
				table.insert(res, towns[math.random(1, #towns)])
			end
			return res
		end
		-- reservoir sampling
		local reservoir = {}
		for i = 1, #towns do
			if i <= params.num then
				reservoir[i] = towns[i]
			else
				local j = math.random(1, i)
				if j <= params.num then
					reservoir[j] = towns[i]
				end
			end
		end
		return reservoir
	end,
	streetsNameScriptFn = function(captureParams, params)
		local streets = nil
		local ok, res = pcall(require, "::/names/europe/en/streets.lua")
		if ok and res then
			streets = res
		else
			local ok2, res2 = pcall(require, "/names/europe/en/streets.lua")
			if ok2 and res2 then
				streets = res2
			end
		end
		if not streets or #streets == 0 then
			return { "High Street", "Station Road", "Main Street", "Church Lane" }
		end
		if params.num < 0 then
			local function shuffle(t)
				local s = {}
				for i = 1, #t do s[i] = t[i] end
				for i = #t, 2, -1 do
					local j = math.random(i)
					s[i], s[j] = s[j], s[i]
				end
				return s
			end
			return shuffle(streets)
		end
		local res = {}
		for k = 1, params.num do
			table.insert(res, streets[math.random(1, #streets)])
		end
		return res
	end,
}
end
''')

# Only map countries that have exact native character name sets in the base game personnameutil.lua.
# All other countries fall back to the base game's neutral international European default ("unitedKingdom"),
# exactly as the base game's built-in europe.names.lua does, avoiding arbitrary or insensitive linguistic conflation.
BASE_GAME_PERSON_NAMES = {
    "france": "france",
    "germany": "germany",
    "italy": "italy",
    "japan": "japan",
    "korea": "korea",
    "norway": "norway",
    "poland": "poland",
    "portugal": "portugal",
    "russia": "russia",
    "spain": "spain",
    "sweden": "sweden",
    "the_netherlands": "netherlands",
    "netherlands": "netherlands",
    "united_kingdom": "unitedKingdom",
    "usa": "usa",
    "china": "china",
    "australia": "australia",
}

def write_tf3_names_lua(filepath: str, display_name: str, path_slug: str, mod_id: str = "ogg_world_names_1") -> None:
    """Writes a native Transport Fever 3 <name>.names.lua definition."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    person_path = BASE_GAME_PERSON_NAMES.get(path_slug, "unitedKingdom")
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write("function data()\n")
        f.write("return {\n")
        f.write(f'\tname = _("{escape_lua_string(display_name)}"),\n')
        f.write("\tpersonNamesScript = {\n")
        f.write('\t\tfileName = "/names/names.script@personNameScriptFn",\n')
        f.write("\t\tparams = {\n")
        f.write(f'\t\t\tpath = "{escape_lua_string(person_path)}",\n')
        f.write("\t\t}\n")
        f.write("\t},\n")
        f.write("\ttownNamesScript = {\n")
        f.write('\t\tfileName = "/names/names.script@townsNameScriptFn",\n')
        f.write("\t\tparams = {\n")
        f.write("\t\t\tlanguages = {\n")
        f.write('\t\t\t\ten = "en",\n')
        f.write('\t\t\t\tfallback = "en",\n')
        f.write("\t\t\t},\n")
        f.write(f'\t\t\tmodId = "{escape_lua_string(mod_id)}",\n')
        f.write(f'\t\t\tpath = "{escape_lua_string(path_slug)}",\n')
        f.write("\t\t}\n")
        f.write("\t},\n")
        f.write("\tstreetNamesScript = {\n")
        f.write('\t\tfileName = "/names/names.script@streetsNameScriptFn",\n')
        f.write("\t\tparams = {\n")
        f.write("\t\t\tlanguages = {\n")
        f.write('\t\t\t\ten = "en",\n')
        f.write('\t\t\t\tfallback = "en",\n')
        f.write("\t\t\t},\n")
        f.write('\t\t\tpath = "europe",\n')
        f.write("\t\t}\n")
        f.write("\t},\n")
        f.write("}\n")
        f.write("end\n")

def write_tf3_mod_manifest(output_dir: str, mod_id: str, mod_name: str, author: str) -> None:
    """Writes the native Transport Fever 3 mod.json and _metadata/modinfo.json."""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. mod.json
    mod_json = {
        "dependencies": None,
        "incompatibilities": None,
        "modId": mod_id,
        "options": None,
        "params": None,
        "postRunScript": { "fileName": "" },
        "preRunScript": { "fileName": "" },
        "revision": 1,
        "runScript": { "fileName": "" },
        "severityAdd": "None",
        "severityRemove": "None"
    }
    with open(os.path.join(output_dir, "mod.json"), "w", encoding="utf-8") as f:
        json.dump(mod_json, f, indent=4)

    # 2. _metadata/modinfo.json
    metadata_dir = os.path.join(output_dir, "_metadata")
    os.makedirs(metadata_dir, exist_ok=True)
    modinfo_json = {
        "authors": [
            {
                "name": author,
                "role": "CREATOR"
            }
        ],
        "description": "Authentic town and city names from GeoNames (CC BY 4.0).",
        "name": mod_name,
        "summary": "Authentic town names for regional gameplay.",
        "tags": [
            "Script Mod"
        ],
        "url": ""
    }
    with open(os.path.join(metadata_dir, "modinfo.json"), "w", encoding="utf-8") as f:
        json.dump(modinfo_json, f, indent=4)

    # 3. _metadata/0.png (Steam Workshop preview image)
    preview_src = os.path.join(os.path.dirname(__file__), "0.png")
    if os.path.exists(preview_src):
        import shutil
        shutil.copyfile(preview_src, os.path.join(metadata_dir, "0.png"))
