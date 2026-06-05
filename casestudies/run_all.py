"""Esegue tutti i casi studio platefeapy in un unico processo Python.

Versione snella: per ogni caso genera SOLO le immagini del 'risultato di
riferimento' (mesh + deformed + 1-2 contour). La convergenza numerica
viene stampata a video ma senza generare immagini per ogni mesh.

Tempo tipico: 2-3 minuti totali.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main():
    print("=" * 78)
    print("  ESECUZIONE DI TUTTI I CASI STUDIO platefeapy")
    print("=" * 78)
    print()
    total_t0 = time.time()

    cases = [
        ("CS01 - Piastra SS Navier",         "cs01_ss_navier"),
        ("CS02 - Piastra incastrata",        "cs02_clamped"),
        ("CS03 - Piastra Levy",              "cs03_levy"),
        ("CS04 - Piastra circolare",         "cs04_circular"),
        ("CS05 - Aspect ratio rettangolare", "cs05_rectangular_aspect"),
        ("CS06 - Patch load centrale",       "cs06_patch_load"),
        ("CS07 - Cantilever plate",          "cs07_cantilever_plate"),
        ("CS08 - Point load centrale",       "cs08_point_load"),
        ("CS09 - Gradiente termico",         "cs09_thermal"),
        ("CS10 - Cedimento vincolare",       "cs10_settlement"),
        ("CS11 - Kirchhoff vs Mindlin",      "cs11_kirchhoff_vs_mindlin"),
        ("CS12 - Patch test",                "cs12_patch_test"),
    ]

    for label, module_name in cases:
        print()
        print("#" * 78)
        print(f"#  {label}  --  {module_name}")
        print("#" * 78)
        t0 = time.time()
        try:
            mod = __import__(module_name)
            mod.main()
        except Exception as exc:
            print(f"  !!! ERRORE in {module_name}: {exc!r}")
            import traceback
            traceback.print_exc()
        dt = time.time() - t0
        print(f"\n  >>> {label} completato in {dt:.1f} s")
        sys.stdout.flush()

    total_dt = time.time() - total_t0
    print()
    print("=" * 78)
    print(f"  TUTTI I CASI COMPLETATI in {total_dt:.1f} s")
    print(f"  Immagini salvate in: {ROOT / 'images'}")
    print("=" * 78)


if __name__ == "__main__":
    main()
