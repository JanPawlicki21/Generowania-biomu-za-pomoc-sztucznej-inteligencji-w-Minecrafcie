"""
Moduł silnika proceduralnego (Procedural Generation Engine).
Odpowiada za tłumaczenie struktur danych wygenerowanych przez AI (LLM) 
na sekwencyjne listy instrukcji wirtualnego środowiska gry Minecraft.
Zawiera mechanizmy mitygacji halucynacji modelu.
"""

from typing import List
from src.domain.plan import BuildingDesign

def sanitize_block(block_name: str) -> str:
    """
    Funkcja weryfikująca i normalizująca materiały budowlane podane przez AI.
    Zabezpiecza silnik gry przed błędami kompilacji w przypadku tzw. halucynacji LLM
    (np. podania nieistniejącego bloku).

    Args:
        block_name (str): Surowa nazwa materiału wygenerowana przez sztuczną inteligencję.

    Returns:
        str: Bezpieczny, zwalidowany identyfikator bloku Minecraft.
    """
    # Ujednolicenie nazwy (czyszczenie formatowania i usuwanie liczby mnogiej)
    name = block_name.lower().strip().replace(" ", "_")
    name = name.replace("slabs", "slab").replace("bricks", "brick").replace("blocks", "block").replace("stairs", "stair")

    # 1. TWARDA BIAŁA LISTA (Rygorystyczna akceptacja poprawnych bloków)
    valid_blocks = {
        "stone_bricks", "smooth_quartz", "blue_concrete", "gray_concrete",
        "white_concrete", "black_concrete", "brown_concrete", "brown_terracotta",
        "oak_planks", "spruce_planks", "dark_oak_planks", "stripped_spruce_log",
        "glass", "gold_block", "glowstone", "sea_lantern",
        "stone_brick_stairs", "quartz_stairs", "bricks", "gravel", "dirt",
        "grass_block", "smooth_stone_slab", "deepslate_tile_slab", "iron_block",
        "polished_blackstone_bricks", "quartz_block", "packed_mud", "sand"
    }

    if name in valid_blocks:
        return name

    # 2. MAPOWANIE HEURYSTYCZNE
    # Tłumaczenie intencji semantycznej AI na bezpieczne odpowiedniki z predefiniowanej palety
    if "glass" in name or "pane" in name or "window" in name: return "glass"
    if "quartz" in name or "marble" in name: return "smooth_quartz"
    if "wood" in name or "log" in name or "timber" in name: return "stripped_spruce_log"
    if "plank" in name or "floor" in name: return "oak_planks"
    if "blackstone" in name: return "polished_blackstone_bricks"
    if "concrete" in name or "cement" in name: return "gray_concrete"
    if "brick" in name or "wall" in name: return "stone_bricks"
    if "terracotta" in name or "coffee" in name or "chocolate" in name: return "brown_terracotta"
    if "slab" in name: return "smooth_stone_slab"
    if "stair" in name or "roof" in name: return "stone_brick_stairs"
    if "iron" in name or "metal" in name or "steel" in name: return "iron_block"
    if "gold" in name: return "gold_block"
    if "dirt" in name or "mud" in name: return "packed_mud"

    # 3. OSTATECZNY FALLBACK (Blok zapasowy w przypadku nierozpoznanego ciągu znaków)
    return "stone_bricks"

def build_dynamic_structure(design: BuildingDesign, zone_type: str = "") -> List[str]:
    """
    Generuje sekwencję komend przestrzennych tworzących strukturę trójwymiarową.
    Oblicza proporcje, integruje oświetlenie, wyznacza strefy interakcji (questowe) 
    oraz aplikuje detale wizerunkowe marki w zależności od typu strefy.

    Args:
        design (BuildingDesign): Model danych reprezentujący projekt architektoniczny AI.
        zone_type (str): Klasyfikacja strefy (np. 'cafe', 'roastery').

    Returns:
        List[str]: Zestaw komend proceduralnych gotowych do wykonania w silniku gry.
    """
    c = []
    
    # Rozpoznanie klasy struktury (Semantic Parsing)
    z_type = str(zone_type).lower() 
    is_cafe = any(kw in z_type for kw in ["cafe", "kawiarnia", "coffee", "sklep", "store", "tchibo"])
    
    # --- EGZEKWOWANIE GRANIC PRZESTRZENNYCH (Spatial Constraints) ---
    w = max(7, min(design.width, 11))
    h = 9 if is_cafe else max(5, min(design.height, 7))
    l = max(7, min(design.length, 11))
    
    # Walidacja materiałów
    wall = sanitize_block(design.wall_material)
    roof = sanitize_block(design.roof_material)
    floor = sanitize_block(design.floor_material)
    glass = sanitize_block(design.window_material)
    
    c.append(f"say [BUILD] Generowanie strefy typu [{z_type}]: {wall} ({w}x{l}x{h})")

    # 1. Konstrukcja bazy (Podmurówka i wylewka)
    c.append(f"fill ~ ~ ~ ~{w-1} ~ ~{l-1} stone_bricks") 
    c.append(f"fill ~1 ~ ~1 ~{w-2} ~ ~{l-2} {floor}") 
    
    # 2. Powłoka architektoniczna (Ściany i rdzenie konstrukcyjne)
    c.append(f"fill ~ ~1 ~ ~{w-1} ~{h} ~{l-1} {wall}")
    c.append(f"fill ~1 ~1 ~1 ~{w-2} ~{h} ~{l-2} air") 
    
    pillar = "stripped_spruce_log"
    c.append(f"fill ~ ~ ~ ~ ~{h+1} ~ {pillar}")
    c.append(f"fill ~{w-1} ~ ~ ~{w-1} ~{h+1} ~ {pillar}")
    c.append(f"fill ~ ~ ~{l-1} ~ ~{h+1} ~{l-1} {pillar}")
    c.append(f"fill ~{w-1} ~ ~{l-1} ~{w-1} ~{h+1} ~{l-1} {pillar}")

    # 3. Przepuszczalność światła (Moduły okienne)
    if w > 4 and l > 4:
        c.append(f"fill ~2 ~2 ~ ~{w-3} ~{h-2} ~ {glass}")      
        c.append(f"fill ~2 ~2 ~{l-1} ~{w-3} ~{h-2} ~{l-1} {glass}") 
        c.append(f"fill ~ ~2 ~2 ~ ~{h-2} ~{l-3} {glass}")      
        c.append(f"fill ~{w-1} ~2 ~2 ~{w-1} ~{h-2} ~{l-3} {glass}") 

    # 4. Moduł wejściowy (Wycinanie ciągów komunikacyjnych)
    door_x = w // 2
    c.append(f"fill ~{door_x} ~1 ~ ~{door_x} ~2 ~ air")
    c.append(f"fill ~{door_x} ~1 ~{l-1} ~{door_x} ~2 ~{l-1} air")

    # 5. Zadaszenie i górne źródła światła
    c.append(f"fill ~-1 ~{h+1} ~-1 ~{w} ~{h+1} ~{l} {roof}")
    c.append(f"fill ~1 ~{h+2} ~1 ~{w-2} ~{h+2} ~{l-2} {roof}")
    c.append(f"fill ~1 ~{h} ~1 ~{w-2} ~{h} ~{l-2} spruce_planks")
    c.append(f"fill ~2 ~{h} ~2 ~{w-3} ~{h} ~{l-3} glowstone") 

    # 6. Integracja systemu grywalizacji (UX) - Marker wejścia
    mid_x, mid_z = w // 2, l // 2
    c.append(f"summon marker ~{mid_x} ~1 ~{mid_z} {{Tags:[\"tchibo_zone_marker\"]}}")

    # 7. Wyposażenie stref specyficznych (Kawiarnia marki)
    if is_cafe:
        # Infrastruktura usługowa (Lada i stacje robocze)
        c.append(f"fill ~1 ~1 ~{l-3} ~{w//2} ~1 ~{l-2} quartz_block") 
        c.append(f"setblock ~2 ~2 ~{l-3} brewing_stand")
        c.append(f"setblock ~1 ~2 ~{l-3} flower_pot")
        
        # Strefa konsumpcji wewnętrznej (Stoliki)
        c.append(f"setblock ~{w-2} ~1 ~2 oak_fence")
        c.append(f"setblock ~{w-2} ~2 ~2 heavy_weighted_pressure_plate")
        c.append(f"setblock ~{w-3} ~1 ~2 oak_stairs[facing=east]")
        
        c.append(f"setblock ~{w-2} ~1 ~4 oak_fence")
        c.append(f"setblock ~{w-2} ~2 ~4 heavy_weighted_pressure_plate")
        c.append(f"setblock ~{w-3} ~1 ~4 oak_stairs[facing=east]")

        # Estetyka wnętrza
        c.append(f"fill ~1 ~1 ~2 ~1 ~3 ~3 bookshelf")
        c.append(f"fill ~2 ~1 ~{mid_z} ~{w-3} ~1 ~{mid_z} blue_carpet")

        # Rozmieszczenie oświetlenia sztucznego
        c.append(f"setblock ~1 ~{h-1} ~1 lantern[hanging=true]")
        c.append(f"setblock ~{w-2} ~{h-1} ~{l-2} lantern[hanging=true]")
        
        # --- ZADASZONY OGRÓDEK NA ZEWNĄTRZ ---
        c.append(f"fill ~-4 ~ ~ ~-1 ~{h} ~{l-1} air") 
        c.append(f"fill ~-4 ~-1 ~ ~-1 ~-1 ~{l-1} stone_bricks") 
        c.append(f"fill ~-4 ~{h} ~ ~-1 ~{h} ~{l-1} {roof}")
        
        c.append(f"fill ~-4 ~ ~ ~-4 ~{h-1} ~ {pillar}")
        c.append(f"fill ~-4 ~ ~{l-1} ~-4 ~{h-1} ~{l-1} {pillar}")
        c.append(f"fill ~-4 ~ ~1 ~-4 ~ ~{l-2} oak_leaves")
        
        # Strefa konsumpcji zewnętrznej
        c.append(f"setblock ~-2 ~ ~2 oak_fence")
        c.append(f"setblock ~-2 ~1 ~2 heavy_weighted_pressure_plate")
        c.append(f"setblock ~-1 ~ ~2 oak_stairs[facing=west]")
        c.append(f"setblock ~-3 ~ ~2 oak_stairs[facing=east]")
        
        c.append(f"setblock ~-2 ~ ~{l-3} oak_fence")
        c.append(f"setblock ~-2 ~1 ~{l-3} heavy_weighted_pressure_plate")
        c.append(f"setblock ~-1 ~ ~{l-3} oak_stairs[facing=west]")
        c.append(f"setblock ~-3 ~ ~{l-3} oak_stairs[facing=east]")
        
        c.append(f"setblock ~-2 ~{h-1} ~2 lantern[hanging=true]")
        c.append(f"setblock ~-2 ~{h-1} ~{l-3} lantern[hanging=true]")

        # 8. Integracja wizerunku marki (Fasadowe Logo 3D)
        if h >= 9:
            start_y = 5
            start_x = door_x - 2 
            
            # Matryca pikselowa (Macromatrix) dla znaku graficznego Tchibo
            logo_matrix = [
                "BGGGB",
                "GBBBG", 
                "BGGBB",
                "GBGGB",
                "BGGBB"  
            ]
            
            c.append("say [INFO] Renderowanie struktury przestrzennej logo...")
            for row_idx, row_str in enumerate(logo_matrix):
                y_coord = start_y + (4 - row_idx) 
                for col_idx, char in enumerate(row_str):
                    x_coord = start_x + col_idx
                    block = "gold_block" if char == 'G' else "blue_concrete"
                    c.append(f"setblock ~{x_coord} ~{y_coord} ~ {block}")
                    
            nbt_format = '{text:\'{"text":"Tchibo","color":"gold","bold":true}\',background:0,Rotation:[180f,0f],transformation:{translation:[0f,0f,0f],scale:[7.0f,7.0f,7.0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}'
            c.append(f"summon text_display ~{door_x - 0.5} ~3.0 ~-0.7 {nbt_format}")
    else:
        # Standardowe wyposażenie dla stref niekomercyjnych
        c.append(f"setblock ~{mid_x} ~1 ~{mid_z} brewing_stand")
        c.append(f"setblock ~{mid_x} ~{h-1} ~{mid_z} lantern[hanging=true]")

    return c

def build_central_plaza(x: int = 0, z: int = 0) -> List[str]:
    """
    Projektuje i kompiluje komendy dla placu centralnego (Hub Area),
    stanowiącego architektoniczny punkt centralny całego wygenerowanego świata.

    Args:
        x (int, optional): Współrzędna X środka placu. Domyślnie 0.
        z (int, optional): Współrzędna Z środka placu. Domyślnie 0.

    Returns:
        List[str]: Skompilowane komendy przestrzenne.
    """
    c = []
    c.append("say [BUILD] Generowanie placu centralnego (Hub Area)...")
    
    # Wyznaczanie promienia i czyszczenie
    c.append(f"fill ~{x-6} ~ ~{z-6} ~{x+6} ~20 ~{z+6} air") 
    c.append(f"fill ~{x-5} ~-1 ~{z-5} ~{x+5} ~-1 ~{z+5} blue_concrete")
    c.append(f"fill ~{x-4} ~-1 ~{z-4} ~{x+4} ~-1 ~{z+4} smooth_quartz")
    
    # Integracja wizualna pozioma (Floor Logo Embedded)
    logo_matrix = [
        "BGGGB",
        "GBBBG", 
        "BGGBB",
        "GBGGB",
        "BGGBB"  
    ]
    
    for row_idx, row_str in enumerate(logo_matrix):
        for col_idx, char in enumerate(logo_matrix[row_idx]):
            target_x = x - 2 + col_idx
            target_z = z - 2 + row_idx
            
            if abs(target_x - x) > 1 or abs(target_z - z) > 1:
                block = "gold_block" if char == 'G' else "blue_concrete"
                c.append(f"setblock ~{target_x} ~-1 ~{target_z} {block}")

    # Obramowanie placu
    c.append(f"fill ~{x-3} ~ ~{z-3} ~{x+3} ~ ~{z-3} quartz_stairs[facing=south]")
    c.append(f"fill ~{x-3} ~ ~{z+3} ~{x+3} ~ ~{z+3} quartz_stairs[facing=north]")
    c.append(f"fill ~{x-3} ~ ~{z-2} ~{x-3} ~ ~{z+2} quartz_stairs[facing=east]")
    c.append(f"fill ~{x+3} ~ ~{z-2} ~{x+3} ~ ~{z+2} quartz_stairs[facing=west]")
    
    # Narożne dominanty i punkty świetlne
    for dx, dz in [(-5, -5), (5, -5), (-5, 5), (5, 5)]:
        c.append(f"setblock ~{x+dx} ~ ~{z+dz} gold_block")
        c.append(f"setblock ~{x+dx} ~1 ~{z+dz} lantern")
        
    return c