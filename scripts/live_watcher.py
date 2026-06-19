import time
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Konfiguracja ścieżki do głównego katalogu projektu
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from src.domain.brief import MarketingBrief
from src.orchestrator import Orchestrator

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv(dotenv_path=project_root / '.env')

# Pobieranie ścieżki do logów z .env (z wartością domyślną jako fallback)
LOG_PATH = os.getenv("MINECRAFT_LOG_PATH", "logs/latest.log")

class MinecraftWatcher:
    """
    Klasa nasłuchująca logi klienta/serwera Minecraft w czasie rzeczywistym.
    Przechwytuje komendy gracza (np. !gen) i inicjuje proces generowania przestrzeni.
    """
    def __init__(self, log_path: str):
        self.log_path = log_path
        
        # Mechanizm debounce: zabezpiecza przed wielokrotnym wyzwoleniem tej samej komendy
        self.last_trigger_time = 0 
        self.cooldown_seconds = 5.0  
        
        try:
            self.orchestrator = Orchestrator(project_root)
        except Exception as e:
            print(f"[CRITICAL ERROR] Inicjalizacja Orchestratora nie powiodła się: {e}")
            sys.exit(1)

        self._print_startup_banner()

    def _print_startup_banner(self):
        """Wyświetla informacje startowe w konsoli (CLI)."""
        print("\n" + "="*60)
        print(" [Live Watcher] System nasłuchiwania logów Minecraft")
        print("="*60)
        print(f" Folder logów: {self.log_path}")
        print(" Użycie w grze: !gen <Nazwa Marki>, <Opis przestrzeni>")
        print("="*60 + "\n")

    def process_command(self, raw_text: str):
        """
        Przetwarza przechwyconą komendę tekstową z logów gry.
        """
        # Weryfikacja cooldownu (debounce)
        current_time = time.time()
        if (current_time - self.last_trigger_time) < self.cooldown_seconds:
            print("[INFO] Zignorowano żądanie (aktywny cooldown).")
            return

        self.last_trigger_time = current_time
        clean_text = raw_text.strip()
        
        if not clean_text: 
            return

        # Parsowanie argumentów (oddzielenie nazwy marki od szczegółowego promptu)
        brand = "Unknown Brand"
        user_prompt = "Domyślny projekt przestrzeni"

        if "," in clean_text:
            parts = clean_text.split(",", 1)
            brand = parts[0].strip()
            user_prompt = parts[1].strip()
        else:
            parts = clean_text.split(" ", 1)
            brand = parts[0].strip()
            if len(parts) > 1:
                user_prompt = parts[1].strip()

        print(f"[NEW REQUEST] Rozpoczęto przetwarzanie komendy:")
        print(f" -> Marka: {brand}")
        print(f" -> Prompt: {user_prompt}")

        try:
            # Inicjalizacja obiektu żądania marketingowego (Brief)
            brief = MarketingBrief(
                brand_name=brand,
                user_request=user_prompt,
                keywords=[],
                tone="Immersive",
                target_audience="Minecraft Players"
            )
            
            print("[INFO] Uruchamianie silnika AI (Generative Pipeline)...")
            self.orchestrator.run_pipeline(brief)
            print("\a") # Sygnał dźwiękowy (BEEP) w systemie Windows po zakończeniu
            
        except Exception as e:
            print(f"[ERROR] Wystąpił błąd podczas generowania projektu: {e}")
            traceback.print_exc()

    def watch(self):
        """
        Główna pętla nasłuchująca zmiany w pliku logów w trybie ciągłym (odpowiednik 'tail -f').
        """
        if not os.path.exists(self.log_path):
            print(f"[ERROR] Nie znaleziono pliku logów pod adresem: {self.log_path}")
            print("[INFO] Upewnij się, że zmienna MINECRAFT_LOG_PATH w pliku .env jest poprawna.")
            return

        print("[INFO] Watcher aktywny. Oczekiwanie na komendy w grze...")
        
        while True:
            try:
                with open(self.log_path, "r", encoding="utf-8", errors='ignore') as f:
                    # Przesunięcie wskaźnika na sam koniec pliku
                    f.seek(0, 2)
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(0.1)
                            continue
                        
                        # Detekcja komendy wyzwalającej z czatu
                        if "!gen" in line:
                            chunks = line.split("!gen", 1)
                            if len(chunks) > 1:
                                self.process_command(chunks[1])
                                
            except Exception as e:
                print(f"[WARNING] Wyjątek w pętli nasłuchującej. Próba restartu... ({e})")
                time.sleep(1)

if __name__ == "__main__":
    watcher = MinecraftWatcher(LOG_PATH)
    watcher.watch()