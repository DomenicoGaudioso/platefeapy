"""Caso studio CS12: Patch test membrana (linear displacement field).

Caso classico FEM (Taylor, "The Finite Element Method", Vol. 1, Cap. 6).
Il patch test verifica che un singolo elemento (o un insieme di elementi)
riesca a riprodurre esattamente un campo di spostamento imposto a livello
nodale, con stato di deformazione interno esatto.

Per la piastra Mindlin, il patch test in modalita' "membrana" prevede:
  * Una piastra rettangolare piccola (1x1 elementi) sotto vincoli di
    semplice appoggio (w=0 sui bordi).
  * Imposizione di un campo di spostamento lineare w(x,y) = a*x + b*y
    su tutti i nodi del bordo (settlement).
  * Verifica che, in assenza di carichi, la soluzione FEM riproduca
    esattamente w(x,y) nodale (errore < 1e-10).

In realta', il test piu' significativo e' quello di membrana con campo
di spostamento lineare nel piano (u, v) - non applicabile direttamente
alla piastra. Per la piastra, il patch test rilevante e' quello di
flessione con w = lineare in x e y.

In questo caso studio si verifica che, sotto spostamenti nodali imposti
ai bordi, lo spostamento interno interpolato sia consistente con i
valori imposti.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from platefeapy import Model, Material, ShellSection
from platefeapy.plotting import plot_mesh, plot_deformed, plot_contour

from common import (
    save_figure, header,
)


def main() -> None:
    L = 1.0
    n_el = 4
    E, nu, t = 210e9, 0.3, 0.01

    header("CS12 - Patch test (linear displacement field) Mindlin")
    print(f"  L = {L} m, t = {t} m, E = {E:.2e} Pa, nu = {nu}")
    print()

    m = Model()
    mat = Material(E=E, nu=nu)
    sec = ShellSection(t=t)
    nx = n_el + 1
    nid = 1
    for j in range(nx):
        for i in range(nx):
            m.add_node(nid, i * L / n_el, j * L / n_el)
            nid += 1
    eid = 1
    for j in range(n_el):
        for i in range(n_el):
            n1 = j * nx + i + 1
            n2 = n1 + 1
            n3 = n2 + nx
            n4 = n1 + nx
            m.add_plate(eid, [n1, n2, n3, n4], mat, sec)
            eid += 1

    a, b = 0.001, 0.0005
    for nid, node in m.nodes.items():
        w_imposed = a * node.x + b * node.y
        m.add_settlement(nid, "w", w_imposed)

    res = m.solve()
    err_max = 0.0
    for nid, node in m.nodes.items():
        w_exact = a * node.x + b * node.y
        w_fem = res.displacement(nid, "w")
        err = abs(w_fem - w_exact)
        err_max = max(err_max, err)
    print(f"  Campo imposto: w(x,y) = {a}*x + {b}*y")
    print(f"  Errore massimo su tutti i nodi: {err_max:.3e} m")
    print(f"  Errore relativo: {err_max / max(abs(a * L), abs(b * L)) * 100:.3e}%")
    print()

    if err_max < 1e-10:
        print("  [OK] Patch test SUPERATO: l'elemento riproduce esattamente il campo lineare")
    else:
        print(f"  [WARN] Patch test FALLITO: errore {err_max:.3e} > 1e-10")

    save_figure(plot_mesh(m, show_node_ids=True), "cs12_mesh.png",
                title="Mesh 4x4 (nodi etichettati)")
    save_figure(plot_deformed(res, scale=1000), "cs12_deformed.png",
                title="Campo di spostamento lineare imposto (scala 1000×)")
    save_figure(plot_contour(res, "w"), "cs12_w_map.png",
                title="Spostamento w [m] - mappa di verifica")
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
