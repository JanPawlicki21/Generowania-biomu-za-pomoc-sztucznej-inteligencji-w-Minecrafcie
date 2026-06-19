"""
Definicje schematów danych (Data Models) dla projektu architektonicznego.
Wykorzystuje bibliotekę Pydantic do walidacji ustrukturyzowanych odpowiedzi (JSON)
zwracanych przez model językowy (LLM) oraz zabezpiecza system przed brakującymi wartościami.
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator, ValidationInfo

class BuildingDesign(BaseModel):
    """
    Parametry fizyczne i materiałowe pojedynczej struktury architektonicznej.
    """
    wall_material: str = Field(..., description="Główny blok użyty do budowy ścian (np. stone_bricks).")
    roof_material: str = Field(..., description="Typ bloku użyty do konstrukcji zadaszenia.")
    floor_material: str = Field(..., description="Typ bloku użyty do wylewki podłogowej.")
    window_material: str = Field(..., description="Typ bloku użyty do przeszkleń.")
    height: int = Field(..., description="Wysokość budynku w blokach.")
    width: int = Field(..., description="Szerokość budynku w blokach (oś X).")
    length: int = Field(..., description="Długość budynku w blokach (oś Z).")
    roof_type: str = Field(..., description="Styl architektoniczny dachu (np. flat, A-frame).")

    @field_validator("wall_material", "roof_material", "floor_material", "window_material", mode="before")
    @classmethod
    def apply_fallbacks_for_missing_materials(cls, v: Any, info: ValidationInfo) -> str:
        """
        Walidator zabezpieczający (Fallback Mechanism).
        Wypełnia braki w danych, jeśli LLM nie wygeneruje wymaganych właściwości materiałowych.
        """
        if v is None:
            defaults = {
                "wall_material": "oak_planks",
                "roof_material": "oak_stairs",
                "floor_material": "cobblestone",
                "window_material": "glass_pane"
            }
            # Zwraca bezpieczną wartość domyślną dla brakującego pola, a w ostateczności blok 'dirt'
            return defaults.get(info.field_name, "dirt")
        return str(v)

class Zone(BaseModel):
    """
    Logiczna i funkcjonalna strefa wygenerowana w świecie gry, zawierająca konkretny budynek.
    """
    zone_type: str = Field(..., description="Klasyfikacja strefy (np. cafe, roastery, plantation).")
    name: str = Field(..., description="Unikalna, opisowa nazwa strefy.")
    purpose: str = Field(..., description="Przeznaczenie marketingowe lub fabularne strefy.")
    design: BuildingDesign = Field(..., description="Szczegółowy projekt architektoniczny budynku w strefie.")

class TerrainSettings(BaseModel):
    """
    Parametry konfiguracyjne dla algorytmów proceduralnego generowania (PCG) topografii wokół stref.
    """
    theme: str = Field(..., description="Główny motyw środowiska (np. Forest, Desert, Industrial).")
    roughness: int = Field(..., description="Amplituda zmian wysokości terenu (wpływ na macierz szumu).")
    vegetation: int = Field(..., description="Gęstość występowania szaty roślinnej (0-10).")
    base_block: str = Field(..., description="Podstawowy blok powierzchniowy (np. grass_block, sand).")
    path_material: str = Field(default="gravel", description="Blok używany do budowy ciągów komunikacyjnych.")

class WorldPlan(BaseModel):
    """
    Główny obiekt agregujący cały wygenerowany przez sztuczną inteligencję plan wirtualnej przestrzeni.
    """
    brand_name: str = Field(..., description="Nazwa promowanej marki.")
    brand_story: Optional[str] = Field(
        default="Witaj w świecie marki.", 
        description="Opcjonalny komunikat powitalny lub narracja związana z marką."
    )
    terrain: TerrainSettings = Field(..., description="Właściwości topograficzne otoczenia.")
    zones: List[Zone] = Field(..., description="Lista wszystkich wygenerowanych stref i budynków.")