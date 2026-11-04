
# 🎮 World Building & In-Game Advertising w Minecraft za pomocą AI

![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)
![Minecraft Version](https://img.shields.io/badge/Minecraft-1.20.1-green.svg)
![AI Model](https://img.shields.io/badge/LLM-Google%20Gemini-orange.svg)

Projekt badawczo-programistyczny zrealizowany w ramach **pracy licencjackiej na Uniwersytecie SWPS**. System służy do zautomatyzowanego, proceduralnego generowania natywnych przestrzeni marketingowych (In-Game Advertising, przypadek użycia: marka Tchibo) w silniku gry Minecraft przy użyciu dużych modeli językowych (LLM).

---

## 💡 O Projekcie

Tradycyjne lokowanie marki w grach wymaga ręcznego projektowania map lub tworzenia zewnętrznych modyfikacji po stronie klienta. Ten projekt rozwiązuje ten problem poprzez:
1. **Tłumaczenie języka naturalnego na architekturę:** Przekształcanie komend tekstowych na ustrukturyzowane plany przestrzenne gry.
2. **Natywne wykonanie:** Generowanie wyjściowych struktur bez konieczności modyfikowania pliku `.jar` gry (wykorzystanie native `Datapacks` oraz skryptów `.mcfunction`).
3. **Automatyzację grywalizacji:** Dynamiczne tworzenie mechanik nagradzania graczy za eksplorację stref marki.

---

## 🛠️ Architektura i Funkcjonalności

* **🧠 LLM Orchestration & JSON Schema:** Integracja z API **Google Gemini**, z wymuszonym ustrukturyzowanym formatem odpowiedzi (JSON Schema) opisującym przestrzeń, materiały i elementy otoczenia.
* **🛡️ Mitigacja Halucynacji & Fallback Engine:** Wbudowany moduł walidujący generowane bloki architektoniczne. W przypadku wykrycia błędnych identyfikatorów bloków silnik automatycznie zamienia je na bezpieczne zamienniki.
* **🏔️ Procedural Content Generation (PCG):** Algorytmy dopasowania terenu, które analizują wysokość (Heightmap) wokół docelowego punktu i wygładzają przestrzeń przed wygenerowaniem obiektu.
* **🏆 Mechanika Grywalizacji (UX):** Automatyczne tworzenie systemów punktacji (`Scoreboard`) i przyznawanie graczym wirtualnych nagród (np. kodów rabatowych) za interakcję ze strefą marki.

---

## 🚀 Technologie

* **Language & Frameworks:** Python 3.11, Pydantic, `google-genai`, `python-dotenv`
* **Game Engine:** Minecraft 1.20.1 (Vanilla / PaperMC)
* **Data Format:** Native NBT Data, Datapacks, `.mcfunction`

---

## 📦 Instalacja i Uruchomienie

### 1. Wymagania wstępne
* Python 3.11+
* Klucz API do Google Gemini (`GEMINI_API_KEY`)
* Zainstalowany Minecraft w wersji 1.20.1

### 2. Sklonuj repozytorium
```bash
git clone https://github.com/JanPawlicki21/Generowania-biomu-za-pomoc-sztucznej-inteligencji-w-Minecrafcie.git
cd Generowania-biomu-za-pomoc-sztucznej-inteligencji-w-Minecrafcie
```

### 3. Skonfiguruj środowisko
```bash
# Utwórz i aktywuj środowisko wirtualne
python -m venv venv
source venv/bin/activate  # Dla Linux/macOS
# lub: venv\Scripts\activate  # Dla Windows

# Zainstaluj zależności
pip install -r requirements.txt
```

### 4. Zmienne środowiskowe
Utwórz plik `.env` w głównym katalogu projektu:
```env
GEMINI_API_KEY=twój_klucz_api_gemini
```

### 5. Uruchomienie skryptu
```bash
python src/main.py
```

---



## 👤 Autor

**Jan Pawlicki**
* LinkedIn: https://www.linkedin.com/in/jan-pawlicki-1a1803426/
* GitHub: [@JanPawlicki21](https://github.com/JanPawlicki21)
