"""
Definicja modeli danych dla zleceń marketingowych (Brief).
Wykorzystuje bibliotekę Pydantic do walidacji danych wejściowych pochodzących 
od użytkownika oraz systemu orkiestracji AI.
"""

from typing import List
from pydantic import BaseModel, Field

class BrandGuidelines(BaseModel):
    """
    Konfiguracja wytycznych wizerunkowych marki.
    """
    subtle_branding: bool = Field(
        default=True, 
        description="Określa, czy lokowanie produktu powinno być dyskretne."
    )
    primary_colors: List[str] = Field(
        default_factory=list, 
        description="Lista głównych kodów kolorystycznych marki."
    )

class MarketingBrief(BaseModel):
    """
    Główny model briefu marketingowego przetwarzanego przez system generatywny.
    """
    brand_name: str = Field(
        ..., 
        description="Nazwa marki promowanej w świecie gry."
    )
    tone: str = Field(
        default="Immersive", 
        description="Styl narracyjny (np. Immersive, Educational, Competitive)."
    )
    user_request: str = Field(
        default="Domyślny projekt", 
        description="Szczegółowy opis wymagań użytkownika dot. struktury."
    )
    keywords: List[str] = Field(
        default_factory=list, 
        description="Słowa kluczowe determinujące estetykę i logikę budynków."
    )
    target_audience: str = Field(
        default="General Minecraft Players", 
        description="Grupa docelowa projektu (persona gracza)."
    )