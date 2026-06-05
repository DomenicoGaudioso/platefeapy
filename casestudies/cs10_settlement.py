"""Caso studio CS10: Cedimento vincolare (support settlement) su piastra SS.

Caso classico FEM. Una piastra quadrata SS, soggetta a pressione uniforme,
presenta un cedimento anelastico imposto a uno dei quattro appoggi (per
esempio l'angolo (0,0)). Tale cedimento genera un campo di spostamento
rigido sovrapposto a quello elastico, e modifica la distribuzione di
momenti flettenti (effetto di subsidenza differenziale).

Caso di studio: piastra 1x1 m SS sui 4 lati, con cedimento w = -0.001 m
impresso al nodo dell'angolo (0,0). Il nodo (0,0) deve spostarsi di -0.001 m
in direzione w (gli altri vincoli SS restano a w=0).

Questo caso e' importante nelle applicazioni ingegneristiche reali:
  * Cedimenti delle fondazioni
  * Subsidenza differenziale in strutture su terreni eterogenei
  * Cedimenti a lungo termine (viscosita', ritiro)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from platefeapy import Model, Material, ShellSection
from platefeapy.plotting import plot_mesh, plot_deformed, plot_contour

from common import (
    rect_plate_mesh, build_ss_bc, save_figure,
    D_bending, header,
)


def main() -> None:
    L = 1.0
    E, nu, t = 210e9, 0.3, 0.01
    p = -1000.0
    delta = -0.001
    D = D_bending(E, nu, t)

    header("CS10 - Piastra SS con cedimento vincolare")
    print(f"  L = {L} m, t = {t} m, E = {E:.2e} Pa, nu = {nu}")
    print(f"  D = {D:.4e} N m, p = {p} Pa, cedimento angolo (0,0) = {delta} m")
    print()

    n_el = 16
    m = Model()
    mat = Material(E=E, nu=nu)
    sec = ShellSection(t=t)
    rect_plate_mesh(m, L, L, n_el, n_el, mat, sec)
    build_ss_bc(m, axis="all")

    n_corner = 1
    m.add_settlement(n_corner, "w", delta)
    for eid in m.elements:
        m.add_pressure(eid, p)
    res = m.solve()

    w_corner = res.displacement(n_corner, "w")
    print(f"  w angolo (0,0)            = {w_corner:.4e} m  (atteso: {delta})")
    print(f"  differenza vs prescritto  = {abs(w_corner - delta):.2e} m")
    print()

    w_max = 0.0
    nid_max = None
    for nid in m.nodes:
        w = abs(res.displacement(nid, "w"))
        if w > w_max:
            w_max = w
            nid_max = nid
    print(f"  w_max nella piastra       = {w_max:.4e} m  (nodo {nid_max})")
    print()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs10_mesh_{n_el}.png",
                title="Mesh con cedimento impresso all'angolo (0,0)")
    save_figure(plot_deformed(res, scale=200), f"cs10_deformed_{n_el}.png",
                title=f"Deformata con cedimento {delta} m (scala 200×)")
    save_figure(plot_contour(res, "w"), f"cs10_w_map_{n_el}.png",
                title="Spostamento w [m] — campo non piu' simmetrico")
    save_figure(plot_contour(res, "Mx"), f"cs10_Mx_{n_el}.png",
                title="Mx [N·m/m]")
    save_figure(plot_contour(res, "My"), f"cs10_My_{n_el}.png",
                title="My [N·m/m]")

    assert abs(w_corner - delta) < 1e-10, "Cedimento non applicato correttamente"
    print(f"  [OK] Cedimento applicato correttamente")
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
