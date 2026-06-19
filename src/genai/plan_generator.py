"""
Moduł integracji z modelem LLM (Google Gemini).
Odpowiada za transformację wytycznych z briefu marketingowego
na ustrukturyzowany, przestrzenny plan świata (JSON) przy użyciu inżynierii promptów.
Zawiera mechanizmy weryfikacji struktury oraz procedury awaryjne (Fallback).
"""

import os
import json
import re
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

from src.domain.brief import MarketingBrief
from src.domain.plan import WorldPlan, Zone, TerrainSettings, BuildingDesign

# Konfiguracja środowiska i ładowanie kluczy z pliku .env
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
load_dotenv(dotenv_path=project_root / '.env')

API_KEY = os.getenv("GOOGLE_API_KEY")

# Inicjalizacja klienta Gemini (pomijana, jeśli system działa w trybie offline)
if API_KEY and API_KEY != "OFFLINE":
    genai.configure(api_key=API_KEY)

def generate_world_plan(brief: MarketingBrief) -> WorldPlan:
    """
    Wysyła zapytanie do modelu LLM w celu wygenerowania planu architektonicznego.
    Wymusza format JSON i weryfikuje minimalne wymagania (np. minimum 3 strefy).
    Posiada wbudowany mechanizm Fallback na wypadek awarii API lub błędu parsowania.

    Args:
        brief (MarketingBrief): Zlecenie zawierające nazwę marki i intencje użytkownika.

    Returns:
        WorldPlan: Zwalidowany i ustrukturyzowany plan świata (Model Pydantic).
    """
    print(f"[INFO] Inicjalizacja silnika AI dla zapytania: '{brief.user_request}'")

    # ==========================================
    # 1. DEFINICJA PLANU AWARYJNEGO (FALLBACK)
    # ==========================================
    # Uruchamiany, gdy brakuje klucza API, połączenia sieciowego lub model zwróci błędny format
    
    default_design = BuildingDesign(
        wall_material="oak_planks", roof_material="oak_stairs", 
        floor_material="stone_bricks", window_material="glass_pane", 
        height=6, width=9, length=9, roof_type="A-frame"
    )
    
    fallback_plan = WorldPlan(
        brand_name=brief.brand_name,
        brand_story="Fallback Mode: System offline. Wczytano projekt domyślny.",
        terrain=TerrainSettings(
            theme="Default", roughness=5, vegetation=5, 
            base_block="grass_block", path_material="gravel"
        ),
        zones=[
            Zone(zone_type="cafe", name="Główna Kawiarnia", purpose="Punkt centralny", design=default_design),
            Zone(zone_type="roastery", name="Palarnia", purpose="Strefa produkcyjna", design=default_design),
            Zone(zone_type="warehouse", name="Magazyn", purpose="Strefa logistyczna", design=default_design)
        ]
    )

    if not API_KEY or API_KEY == "OFFLINE": 
        print("[WARNING] System operuje w trybie OFFLINE. Zwracam plan awaryjny.")
        return fallback_plan

    # ==========================================
    # 2. INŻYNIERIA PROMPTU (System Prompt Injection)
    # ==========================================
    
    models = ["models/gemini-2.5-flash"]

    prompt = f"""
    Jesteś ekspertem ds. inżynierii przestrzennej i architektury proceduralnej Minecraft.
    Twoim zadaniem jest wygenerowanie struktury przestrzennej (WorldPlan) dla marki: "{brief.brand_name}".
    Wytyczne projektowe: "{brief.user_request}".
    
    ZASADA KRYTYCZNA:
    Musisz wygenerować MINIMUM 3 unikalne budynki w tablicy "zones". Jest to twardy wymóg systemowy.
    
    FORMAT WYJŚCIOWY:
    Odpowiedź musi być CZYSTYM KODEM JSON. Nie dodawaj żadnych opisów, wstępów ani znaczników markdown poza samym JSON-em.
    
    SZABLON JSON:
    {{
      "brand_name": "{brief.brand_name}",
      "terrain": {{
        "theme": "Forest", "roughness": 3, "vegetation": 8,
        "base_block": "grass_block", "path_material": "cobblestone"
      }},
      "zones": [
        {{
          "zone_type": "cafe", "name": "Kawiarnia", "purpose": "Relaks",
          "design": {{
             "wall_material": "bricks", "roof_material": "stone_brick_stairs",
             "floor_material": "oak_planks", "window_material": "glass",
             "height": 6, "width": 10, "length": 10, "roof_type": "flat"
          }}
        }}
      ]
    }}
    """

    # ==========================================
    # 3. KOMUNIKACJA Z API I PARSOWANIE WYNIKÓW
    # ==========================================
    
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            # Ekstrakcja danych JSON za pomocą wyrażeń regularnych (zabezpieczenie przed tekstem wokół JSONa)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            
            if match:
                data = json.loads(match.group(0))
                if "terrain" not in data: 
                    continue
                
                # Inicjalizacja modelu zwalidowanych danych
                plan = WorldPlan(**data)
                
                # --- MITYGACJA BŁĘDÓW LLM (Kompensacja brakujących stref) ---
                while len(plan.zones) < 3:
                    print(f"[WARNING] Detekcja ubytku danych: LLM wygenerował tylko {len(plan.zones)} stref. Inicjalizacja kompensacji...")
                    missing_idx = len(plan.zones) + 1
                    
                    # Klonowanie parametrów architektonicznych z pierwszej wygenerowanej strefy lub fallbacku
                    new_design = plan.zones[0].design if plan.zones else default_design
                    
                    extra_zone = Zone(
                        zone_type=f"extra_zone_{missing_idx}",
                        name=f"Strefa Kompensacyjna {missing_idx}",
                        purpose="Support Infrastructure",
                        design=new_design
                    )
                    plan.zones.append(extra_zone)

                print(f"[SUCCESS] Deserializacja zakończona. Wygenerowano łącznie: {len(plan.zones)} budynków. (Model: {model_name})")
                return plan

        except Exception as e:
            print(f"[ERROR] Błąd przetwarzania odpowiedzi modelu {model_name}: {e}")
            continue 

    print("[WARNING] Wszystkie próby wygenerowania planu zawiodły. Wczytywanie planu awaryjnego.")
    return fallback_plan