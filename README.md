# World Building w Minecraft za pomocą AI ☕
**Proceduralna integracja marki Tchibo w silniku gry (In-Game Advertising)**

Projekt badawczo-programistyczny zrealizowany w ramach pracy licencjackiej na Uniwersytecie SWPS. 
System wykorzystuje modele generatywnej sztucznej inteligencji (LLM) do dynamicznego, zautomatyzowanego generowania natywnych przestrzeni marketingowych wewnątrz gry Minecraft, bez konieczności używania zewnętrznych modyfikacji po stronie klienta.

## ⚙️ Architektura i Funkcjonalności
* 🧠 **LLM Orchestration:** Integracja z API Google Gemini 2.5 Flash, tłumacząca w locie polecenia języka naturalnego na ustrukturyzowane plany przestrzenne (JSON Schema).
* 🛡️ **Mitygacja Halucynacji:** Wbudowane mechanizmy walidacji materiałów architektonicznych (Fallback) zapobiegające błędom kompilacji silnika Minecrafta.
* 🎮 **System Grywalizacji (UX):** Zautomatyzowany mechanizm *Datapacków* ładujący system punktacji (Scoreboard) oraz przyznający graczom wirtualne nagrody (kody rabatowe) za eksplorację stref.
* 🗺️ **Procedural Content Generation (PCG):** Algorytmy wygładzania mapy wysokości oraz adaptacji terenu wokół generowanych kawiarni.

## 🛠️ Technologie
* **Python 3.11** (`pydantic`, `google-generativeai`, `python-dotenv`)
* **Minecraft 1.20.1** (Silnik renderujący, mcfunctions, NBT data)

## 🚀 Jak uruchomić projekt lokalnie

1. **Sklonuj repozytorium**
2. **Utwórz środowisko wirtualne i zainstaluj pakiety:**
   ```bash
   pip install -r requirements.txt