"""
Moduł odpowiedzialny za generowanie ciągów komunikacyjnych (ścieżek) pomiędzy strefami.
Wykorzystuje algorytm trasowania L-shape (najpierw oś X, potem oś Z) z uwzględnieniem
fundamentów podtrzymujących, wyrównania terenu oraz proceduralnego oświetlenia.
"""

from typing import List

def build_connection_path(x1: int, z1: int, x2: int, z2: int, material: str = "stone_bricks") -> List[str]:
    """
    Generuje listę komend Minecraft łączących dwa punkty na mapie za pomocą ścieżki.

    Algorytm buduje ścieżkę w kształcie litery 'L', zapewniając odpowiedni fundament
    (aby zapobiec opadaniu bloków grawitacyjnych, takich jak żwir lub piasek) oraz
    czyszcząc przestrzeń nad nią w celu umożliwienia swobodnego przejścia gracza.

    Args:
        x1 (int): Współrzędna X punktu startowego.
        z1 (int): Współrzędna Z punktu startowego.
        x2 (int): Współrzędna X punktu docelowego.
        z2 (int): Współrzędna Z punktu docelowego.
        material (str, optional): ID bloku z którego wykonana jest nawierzchnia. Domyślnie "stone_bricks".

    Returns:
        List[str]: Zestaw surowych komend /fill oraz /setblock.
    """
    cmds = []
    
    # Wyznaczanie wartości brzegowych do blokowych komend /fill
    start_x, end_x = min(x1, x2), max(x1, x2)
    start_z, end_z = min(z1, z2), max(z1, z2)

    # ==========================================
    # 1. ODCINEK WZDŁUŻ OSI X (Wschód - Zachód)
    # ==========================================
    
    # A. Fundament podtrzymujący (Ziemia) - wypełnia ewentualne dziury i doliny w terenie
    cmds.append(f"fill ~{start_x} ~-5 ~{z1-1} ~{end_x} ~-1 ~{z1+1} dirt replace air")
    
    # B. Właściwa nawierzchnia ścieżki (Szerokość: 3 bloki)
    cmds.append(f"fill ~{start_x} ~-1 ~{z1-1} ~{end_x} ~-1 ~{z1+1} {material}")
    
    # C. Czyszczenie przestrzeni nad ścieżką (Headroom - 10 bloków wzwyż)
    cmds.append(f"fill ~{start_x} ~ ~{z1-1} ~{end_x} ~10 ~{z1+1} air")
    
    # ==========================================
    # 2. ODCINEK WZDŁUŻ OSI Z (Północ - Południe)
    # ==========================================
    
    # A. Fundament podtrzymujący
    cmds.append(f"fill ~{x2-1} ~-5 ~{start_z} ~{x2+1} ~-1 ~{end_z} dirt replace air")
    
    # B. Właściwa nawierzchnia ścieżki
    cmds.append(f"fill ~{x2-1} ~-1 ~{start_z} ~{x2+1} ~-1 ~{end_z} {material}")
    
    # C. Czyszczenie przestrzeni nad ścieżką
    cmds.append(f"fill ~{x2-1} ~ ~{start_z} ~{x2+1} ~10 ~{end_z} air")
    
    # ==========================================
    # 3. PROCEDURALNE OŚWIETLENIE (Latarnie)
    # ==========================================
    
    dist_x = abs(x2 - x1)
    
    # Generowanie latarni co 8 bloków, jeśli odcinek X jest wystarczająco długi
    if dist_x > 8:
        step = 1 if x2 > x1 else -1
        for bx in range(x1, x2, step * 8):
            # Podstawa: drewniany słupek (płotek)
            cmds.append(f"setblock ~{bx} ~ ~{z1+2} oak_fence")
            # Źródło światła: latarnia zawieszona na słupku
            cmds.append(f"setblock ~{bx} ~1 ~{z1+2} lantern")

    return cmds