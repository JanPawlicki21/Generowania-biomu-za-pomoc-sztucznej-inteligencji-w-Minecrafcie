import os
import math
import traceback
import random 
from pathlib import Path
from dotenv import load_dotenv

from src.domain import plan
from src.domain.brief import MarketingBrief
from src.genai.plan_generator import generate_world_plan
from src.builder.mcfunction_builder import write_datapack
from src.builder.terrain_builder import build_smart_terrain
from src.builder.path_builder import build_connection_path 
from src.builder.procedural_builder import sanitize_block 
from src.builder.procedural_builder import build_dynamic_structure, build_central_plaza

class Orchestrator:
    def __init__(self, project_root: Path):
        self.root = project_root
        load_dotenv(dotenv_path=project_root / '.env')
        
        save_path_str = os.getenv("MINECRAFT_SAVE_PATH")
        if save_path_str:
            path_obj = Path(save_path_str)
            if path_obj.name == "datapacks":
                self.target_dir = path_obj
            else:
                self.target_dir = path_obj / "datapacks"
            self.target_dir.mkdir(parents=True, exist_ok=True)
            print(f"CEL ZAPISU: {self.target_dir}")
        else:
            self.target_dir = self.root / "generated_datapacks"

    def run_pipeline(self, brief: MarketingBrief):
        print(f"Generowanie świata TCHIBO: {brief.brand_name}")
        
        try:
            # 1. AI generuje plan
            plan = generate_world_plan(brief)
            
            # 2. Tworzenie folderów
            pack_path = write_datapack(self.target_dir, plan)
            
            # 3. Wiadomość powitalna
            self._create_on_load_message(pack_path, plan, brief)
            
            # 4. Setup World
            print("  🔨 Generowanie setup_world.mcfunction...")
            self._create_setup_world(pack_path, plan)
            
            print(f" GOTOWE! Raport zapisany w: {pack_path}")
            print(f" TERAZ WPISZ W GRZE: /reload")

        except Exception as e:
            print(f"\nBŁĄD W ORCHESTRATORZE ")
            print(f"Opis błędu: {e}")
            traceback.print_exc()
            print("Błąd biom nie został wygenerowany!!!\n")

    def _create_on_load_message(self, pack_path: Path, plan, brief: MarketingBrief):
        on_load_file = pack_path / "data" / "tchibo" / "functions" / "on_load.mcfunction"
        user_req = getattr(brief, 'user_request', "Auto")
        
        cmds = []
        cmds.append('tellraw @a ["", {"text":"\\n================================\\n", "color":"dark_gray"}]')
        cmds.append(f'tellraw @a ["", {{"text":" 🏗️ Wygenerowano: ", "color":"gray"}}, {{"text":"{len(plan.zones)} budynki", "color":"aqua", "bold":true}}]')
        
        click_cmd = "/function tchibo:setup_world"
        cmds.append(f'tellraw @a ["", {{"text":"\\n   >>> ", "color":"white"}}, {{"text":"[KLIKNIJ ABY ZBUDOWAĆ]", "color":"green", "bold":true, "clickEvent":{{"action":"run_command", "value":"{click_cmd}"}}}}, {{"text":" <<<\\n", "color":"white"}}]')
        
        on_load_file.write_text("\n".join(cmds), encoding="utf-8")

    def _create_setup_world(self, pack_path: Path, plan):
        function_file = pack_path / "data" / "tchibo" / "functions" / "setup_world.mcfunction"
        
        cmds = []
        cmds.append('title @a title {"text":"GEN-AI BUILD","color":"gold"}')
        cmds.append('say [DEBUG] 1. Rozpoczynam budowę terenu...')

   # --- RESET SYSTEMU QUESTA PRZED NOWYM BUDOWANIEM ---
        cmds.append('scoreboard objectives add tchibo_quest dummy "Zebrane Ziarna"')
        cmds.append('scoreboard objectives setdisplay sidebar tchibo_quest')
        cmds.append('kill @e[type=marker,tag=tchibo_zone_marker]')
        cmds.append('scoreboard players set @a tchibo_quest 0') # <-- ZMIANA NA SET 0
        cmds.append('tag @a remove rabat_przyznany')

        # --- ZABEZPIECZENIE TERENU PRZED HALUCYNACJAMI AI ---
        plan.terrain.base_block = sanitize_block(getattr(plan.terrain, 'base_block', 'stone_bricks'))
        plan.terrain.path_material = sanitize_block(getattr(plan.terrain, 'path_material', 'gravel'))

        # 1. Teren
        cmds.extend(build_smart_terrain(160, 160, plan.terrain, []))

        # 2. Pozycje (Koło)
        num_zones = len(plan.zones)
        positions = []
        radius = 45 
        
        if num_zones > 0:
            angle_step = 360 / num_zones
            for i in range(num_zones):
                angle_rad = math.radians(i * angle_step)
                x = int(radius * math.cos(angle_rad))
                z = int(radius * math.sin(angle_rad))
                positions.append((x, z))

        path_mat = sanitize_block(getattr(plan.terrain, 'path_material', 'gravel'))
        base_mat = sanitize_block(plan.terrain.base_block)
        
        cmds.append('say [DEBUG] 2. Budowa stref i budynków...')

        for i, zone in enumerate(plan.zones):
            if i < len(positions): x, z = positions[i]
            else: x, z = (0, 60 + (i*10))

            w = max(5, zone.design.width)
            l = max(5, zone.design.length)
            
            cmds.append(f'say [DEBUG] Strefa {i+1}: {zone.name}...')

            # A. OCZYSZCZANIE i PODŁOGA
            cmds.append(f"fill ~{x-2} ~ ~{z-2} ~{x+w+2} ~20 ~{z+l+2} air")
            cmds.append(f"fill ~{x-2} ~-1 ~{z-2} ~{x+w+2} ~-1 ~{z+l+2} {base_mat}")

            target_x = x + (w // 2)
            target_z = z - 1 if z >= 0 else z + l

            # B. ŚCIEŻKA DO DRZWI
            cmds.extend(build_connection_path(6, 6, target_x, target_z, path_mat))
            
            # C. BUDYNEK (Spłaszczanie egzekucji)
            z_type = zone.zone_type.lower()
            building_cmds = build_dynamic_structure(zone.design, z_type)
            
            for cmd in building_cmds:
                cmds.append(f"execute positioned ~{x} ~-1 ~{z} run {cmd}")
            
            # Tabliczka (oczyszczona, bez dublowania)
            safe_name = zone.name.replace('"', '').replace("'", "")
            sign_json = f'\'{{\"text\":\"{safe_name}\",\"color\":\"blue\",\"bold\":true}}\''
            rot = "8" if target_z < z else "0"
            cmds.append(f"setblock ~{target_x+1} ~ ~{target_z} oak_sign[rotation={rot}]{{front_text:{{messages:[{sign_json},'\"\"','\"\"','\"\"']}}}}")

        # 3. PLAC CENTRALNY (Przeniesiony na sam koniec!)
        cmds.append('say [DEBUG] 3. Rysowanie placu głównego i logo na wierzchu...')
        cmds.append("fill ~-3 ~-1 ~-3 ~3 ~-1 ~3 stone_bricks")
        cmds.append("setblock ~ ~1 ~ beacon")
        cmds.extend(build_central_plaza(0, 0))

        cmds.append('title @a title {"text":"GOTOWE!","color":"green"}')
        cmds.append('say [DEBUG] Proces zakończony sukcesem.')
        
        function_file.write_text("\n".join(cmds), encoding="utf-8") 

     # 4. ZŁOTE KOLUMNY REKLAMOWE WOKÓŁ PLACU
        cmds.append('say [DEBUG] 4. Generowanie zlotych kolumn z hologramem...')
        
        banner_positions = [(-7, -7), (7, -7), (-7, 7), (7, 7)]
        
        for rx, rz in banner_positions:
            # Konstrukcja z 2 bloków złota
            cmds.append(f"setblock ~{rx} ~ ~{rz} gold_block")
            cmds.append(f"setblock ~{rx} ~1 ~{rz} gold_block")
            
            # Pływający hologram - powiększony 3x i zabezpieczony potrójnym cudzysłowem w Pythonie
            holo_nbt = """{text:'{"text":"TCHIBO","color":"aqua","bold":true}',billboard:"center",transformation:{translation:[0f,0f,0f],scale:[3f,3f,3f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}"""
            cmds.append(f"summon text_display ~{rx+0.5} ~3.0 ~{rz+0.5} {holo_nbt}")