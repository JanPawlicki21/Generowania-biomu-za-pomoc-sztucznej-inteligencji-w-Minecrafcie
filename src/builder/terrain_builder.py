"""
Moduł odpowiedzialny za proceduralne generowanie topografii terenu (Procedural Terrain Generation).
Tworzy zróżnicowaną rzeźbę terenu za pomocą algorytmów wygładzania szumu,
zarządza warstwami geologicznymi oraz dystrybucją roślinności z zachowaniem stref wykluczenia dla budynków.
"""

import random
from typing import List, Tuple
from src.domain.plan import TerrainSettings

def build_smart_terrain(width: int, length: int, settings: TerrainSettings, buildings_pos: List[Tuple[int, int]]) -> List[str]:
    """
    Generuje sekwencję komend kształtujących krajobraz (topografię oraz florę).

    Algorytm wykorzystuje macierz szumu poddaną iteracyjnemu wygładzaniu w celu 
    symulacji naturalnych wzniesień i dolin. Automatycznie dobiera bloki fundamentowe
    oraz gatunki roślinności na podstawie wytycznych wygenerowanych przez AI.

    Args:
        width (int): Szerokość obszaru generowania w blokach (oś X).
        length (int): Długość obszaru generowania w blokach (oś Z).
        settings (TerrainSettings): Obiekt zawierający parametry terenu (m.in. chropowatość, gęstość zalesienia).
        buildings_pos (List[Tuple[int, int]]): Lista współrzędnych (X, Z) planowanych budowli, tworząca strefy wykluczenia (Exclusion Zones).

    Returns:
        List[str]: Zestaw skompilowanych komend przestrzennych (/fill, /place feature) dla silnika gry.
    """
    c = []
    
    # ==========================================
    # 1. GENEROWANIE MAPY WYSOKOŚCI (Heightmap Generation)
    # ==========================================
    
    # Inicjalizacja macierzy losowym szumem bazowym (Base Noise)
    heightmap = {}
    for x in range(-width//2, width//2, 4):
        for z in range(-length//2, length//2, 4):
            noise = random.randint(-settings.roughness, settings.roughness)
            heightmap[(x, z)] = noise

    # Iteracyjne wygładzanie szumu (Smoothing / Matrix Blur) dla uzyskania naturalnych zboczy
    for _ in range(2):
        new_map = heightmap.copy()
        for x in range(-width//2, width//2, 4):
            for z in range(-length//2, length//2, 4):
                total, count = 0, 0
                for dx in [-4, 0, 4]:
                    for dz in [-4, 0, 4]:
                        val = heightmap.get((x+dx, z+dz))
                        if val is not None:
                            total += val
                            count += 1
                if count > 0: 
                    new_map[(x, z)] = int(total / count)
        heightmap = new_map

    # ==========================================
    # 2. MAPOWANIE WARSTW GEOLOGICZNYCH I EKOSYSTEMU
    # ==========================================
    
    base_block = settings.base_block
    
    # Walidacja semantyczna powłoki wierzchniej
    if base_block == "grass": 
        base_block = "grass_block"
    
    # Dobór materiału fundamentowego (Sub-layer) na podstawie bloku wierzchniego
    fill_block = "dirt"
    if "sand" in base_block: 
        fill_block = "sandstone"
    if "snow" in base_block: 
        fill_block = "snow_block"

    # Mapowanie typu zalesienia (Biome Feature Mapping) do standardu Minecraft 1.20+
    tree_type = "minecraft:oak"
    if "spruce" in base_block: 
        tree_type = "minecraft:spruce"
    if "jungle" in base_block: 
        tree_type = "minecraft:jungle_tree"
    if "acacia" in base_block: 
        tree_type = "minecraft:acacia"
    if "birch" in base_block: 
        tree_type = "minecraft:birch"
    if "cherry" in base_block: 
        tree_type = "minecraft:cherry"

    # ==========================================
    # 3. KOMPILACJA KOMEND PRZESTRZENNYCH (Volume Rendering)
    # ==========================================
    
    for x in range(-width//2, width//2, 4):
        for z in range(-length//2, length//2, 4):
            offset = heightmap[(x, z)]
            
            # Renderowanie fundamentów (od Y=-30 do poziomu gruntu) relatywnie do gracza (~)
            c.append(f"fill ~{x} ~-30 ~{z} ~{x+3} ~{offset-1} ~{z+3} {fill_block}")
            
            # Renderowanie powłoki wierzchniej
            c.append(f"fill ~{x} ~{offset} ~{z} ~{x+3} ~{offset} ~{z+3} {base_block}")
            
            # Weryfikacja stref wykluczenia (Exclusion Zones) wokół planowanych budynków
            is_clear = True
            for (bx, bz) in buildings_pos:
                distance = ((x - bx)**2 + (z - bz)**2)**0.5
                if distance < 15:
                    is_clear = False
                    break
            
            # Proceduralna dystrybucja szaty roślinnej na podstawie progu parametru vegetation
            if is_clear and random.randint(0, 100) < settings.vegetation * 2:
                c.append(f"place feature {tree_type} ~{x} ~{offset+1} ~{z}")

    return c