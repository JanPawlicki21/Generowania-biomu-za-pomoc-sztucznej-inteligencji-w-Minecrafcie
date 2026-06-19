"""
Moduł odpowiedzialny za generowanie fizycznej struktury datapacka w środowisku Minecraft.
Tłumaczy zaplanowane przez AI strefy (WorldPlan) na gotowe pliki tekstowe .mcfunction,
oraz zarządza inicjalizacją mechanizmów wewnątrz gry (system questów, pętla tick).
"""

import os
import shutil
from pathlib import Path
from typing import List

from src.domain.plan import WorldPlan
from src.builder.procedural_builder import build_dynamic_structure

def write_datapack(target_directory: Path, plan: WorldPlan) -> Path:
    """
    Tworzy kompletny datapack, generując budynki dynamicznie na podstawie projektu AI.

    Args:
        target_directory (Path): Ścieżka docelowa do zapisu wygenerowanych plików.
        plan (WorldPlan): Struktura danych reprezentująca projekt wygenerowany przez LLM.

    Returns:
        Path: Pełna ścieżka do wygenerowanego folderu datapacka.
    """
    
    brand_name = plan.brand_name
    pack_name = "tchibo_genai"
    full_path = target_directory / pack_name
    namespace = "tchibo"

    # 1. Czyszczenie starego folderu
    if full_path.exists():
        try:
            shutil.rmtree(full_path)
        except Exception as e:
            print(f"[WARNING] Nie udało się usunąć starego folderu: {e}")

    # 2. Tworzenie struktury folderów
    functions_dir = full_path / "data" / namespace / "functions"
    tags_dir = full_path / "data" / "minecraft" / "tags" / "functions"
    
    functions_dir.mkdir(parents=True, exist_ok=True)
    tags_dir.mkdir(parents=True, exist_ok=True)

    # 3. Plik pack.mcmeta (Definicja paczki)
    pack_mcmeta = f"""
    {{
        "pack": {{
            "pack_format": 15,
            "description": "System GenAI Integracji Marki - {brand_name}"
        }}
    }}
    """
    (full_path / "pack.mcmeta").write_text(pack_mcmeta, encoding="utf-8")

    # 4. Meta-tagi i pliki inicjalizacyjne (load oraz tick)
    load_json = f"""
    {{
        "values": [
            "{namespace}:on_load"
        ]
    }}
    """
    (tags_dir / "load.json").write_text(load_json, encoding="utf-8")
    
    tick_json = f"""
    {{
        "values": [
            "{namespace}:tick"
        ]
    }}
    """
    (tags_dir / "tick.json").write_text(tick_json, encoding="utf-8")
    
    # --- 4A. Plik on_load - tworzy tabele wynikow dla questa ---
    on_load_content = r"""say Ladowanie systemu wsparcia marki...
scoreboard objectives add tchibo_quest dummy "Zebrane Ziarna"
scoreboard objectives setdisplay sidebar tchibo_quest
"""
    (functions_dir / "on_load.mcfunction").write_text(on_load_content, encoding="utf-8")

    # --- 4B. Plik tick - wykonuje sie 20 razy na sekunde (Logika grywalizacji) ---
    tick_content = r"""# A. Daje ksiazke startowa z historia (tylko raz na gracza)
execute as @a[tag=!tchibo_book] run give @s written_book{title:"Historia",author:"Tchibo",pages:['{"text":"Witaj w swiecie Tchibo! Nasza historia zaczyna sie w 1949 roku w Hamburgu, kiedy to wpadlismy na pomysl wysylkowej sprzedazy kawy."}','{"text":"Slowo Tchibo to zgrabne polaczenie nazwiska jednego z zalozycieli (Tchiling) oraz niemieckiego slowa oznaczajacego ziarno (Bohne)."}']} 1
tag @a[tag=!tchibo_book] add tchibo_book

# B. MECHANIZM ZBIERANIA PUNKTOW (Wejscie do generowanego budynku)
execute as @e[type=marker,tag=tchibo_zone_marker] at @s if entity @a[distance=..5] run scoreboard players add @a[distance=..5,limit=1] tchibo_quest 1
execute as @e[type=marker,tag=tchibo_zone_marker] at @s if entity @a[distance=..5] run title @a[distance=..5] actionbar {"text":"+1 Ziarno Kawy! Odwiedzono strefe!","color":"green","bold":true}
execute as @e[type=marker,tag=tchibo_zone_marker] at @s if entity @a[distance=..5] run playsound minecraft:entity.experience_orb.pickup master @a[distance=..5]
execute as @e[type=marker,tag=tchibo_zone_marker] at @s if entity @a[distance=..5] run kill @s

# C. SYSTEM NAGRODY: 3 punkty = Kupon Rabatowy
execute as @a[scores={tchibo_quest=3..},tag=!rabat_przyznany] run give @s paper{display:{Name:'{"text":"KUPON RABATOWY -10%","color":"gold","bold":true}',Lore:['{"text":"Zrealizuj kod na Tchibo.pl:","color":"gray"}','{"text":"TCHIBO-MINECRAFT-2026","color":"white","bold":true}']}} 1
execute as @a[scores={tchibo_quest=3..},tag=!rabat_przyznany] run title @s title {"text":"GRATULACJE!","color":"gold","bold":true}
execute as @a[scores={tchibo_quest=3..},tag=!rabat_przyznany] run playsound minecraft:entity.player.levelup master @s
execute as @a[scores={tchibo_quest=3..},tag=!rabat_przyznany] run tag @s add rabat_przyznany
"""
    (functions_dir / "tick.mcfunction").write_text(tick_content, encoding="utf-8")

    # 5. Generowanie budynków na podstawie projektu AI
    print("[INFO] Budowanie struktur .mcfunction na podstawie projektu AI...")

    for zone in plan.zones:
        z_type = zone.zone_type.lower()
        filename = "build_unknown.mcfunction"
        
        if "cafe" in z_type:
            filename = "build_cafe.mcfunction"
        elif "origin" in z_type or "plant" in z_type:
            filename = "build_plantation.mcfunction"
        elif "process" in z_type or "roast" in z_type:
            filename = "build_roastery.mcfunction"
            
        # Sanityzacja i budowanie struktury
        if zone.design:
            commands = build_dynamic_structure(zone.design, z_type)
            (functions_dir / filename).write_text("\n".join(commands), encoding="utf-8")
        else:
            print(f"[WARNING] Strefa {zone.name} nie posiada zdefiniowanego projektu (design)!")

    return full_path