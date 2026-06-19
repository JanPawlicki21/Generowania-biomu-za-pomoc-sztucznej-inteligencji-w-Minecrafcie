"""
Skrypt inicjalizujący główny rurociąg (pipeline) generatywnej sztucznej inteligencji.
Służy do bezpośredniego testowania procesu generowania przestrzeni z poziomu konsoli,
bez konieczności uruchamiania nasłuchiwacza logów (Live Watchera).
"""

import sys
import traceback
from pathlib import Path

# Konfiguracja ścieżki absolutnej do katalogu głównego projektu
# Zapewnia poprawne importy modułów z katalogu 'src' niezależnie od miejsca uruchomienia skryptu
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.domain.brief import MarketingBrief
from src.orchestrator import Orchestrator

def main():
    """
    Główna funkcja wykonawcza skryptu.
    Symuluje odebranie wytycznych marketingowych (briefu) i uruchamia proces orkiestracji.
    """
    print("\n" + "="*50)
    print(" [Main Pipeline] Tryb Standalone")
    print("="*50)
    print("[INFO] Inicjalizacja żądania marketingowego...")

    # 1. Przygotowanie struktury danych wejściowych (Brief)
    # Parametry symulujące wytyczne, które docelowo pochodzą z czatu gry
    brief = MarketingBrief(
        brand_name="Tchibo",
        user_request="Elegancka kawiarnia i strefa relaksu w otoczeniu natury",
        keywords=["coffee", "nature", "industry", "home"],
        tone="Immersive",
        target_audience="Minecraft Players"
    )

    try:
        # 2. Inicjalizacja rdzenia systemu i uruchomienie generowania
        app = Orchestrator(ROOT_DIR)
        
        print(f"[INFO] Przekazanie briefu (Marka: {brief.brand_name}) do silnika AI.")
        app.run_pipeline(brief)
        
        print("[SUCCESS] Pipeline zakończył działanie bez błędów.")
        
    except Exception as e:
        print(f"[CRITICAL ERROR] Awaria w głównym procesie generowania: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()