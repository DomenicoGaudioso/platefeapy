"""Caso studio CS06: Carico parziale (patch load) su piastra SS.

Caso classico (Timoshenko, "Theory of Plates and Shells", §3, p. 124 e Tab. 5).
Piastra quadrata SS con un carico uniforme p applicato solo su una sotto-area
centrale di lato c < L. La soluzione dipende dal rapporto c/L.

Caso benchmark tipico: piastra LxL, SS su tutti i lati, con carico q agente su
una piastra centrale di lato c = L/2. Si usa il coefficiente tabulato in
Timoshenko per il caso "central patch load" con c/L = 0.5.

Per c/L = 0.5 e nu = 0.3 (Timoshenko tab. 5, p. 124, paragrafo "concentrated
load distributed over small area"), il coefficiente vale approssimativamente:

    w_max(0,0) = 0.00743 * q * L^4 / D

(per piastra SS, carico uniforme su quadrato centrale di lato L/2, sotto
l'azione del carico stesso).
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
    rect_plate_mesh, build_ss_bc, save_figure,
    D_bending, print_check, header,
)


def main() -> None:
    L = 1.0
    E, nu, t = 210e9, 0.3, 0.01
    p = -1000.0
    D = D_bending(E, nu, t)
    c = 0.5

    n_el = 32
    m = Model()
    mat = Material(E=E, nu=nu)
    sec = ShellSection(t=t)
    rect_plate_mesh(m, L, L, n_el, n_el, mat, sec)
    build_ss_bc(m, axis="all")

    x0 = (L - c) / 2.0
    x1 = (L + c) / 2.0
    y0 = (L - c) / 2.0
    y1 = (L + c) / 2.0

    elems_inside = 0
    for eid, el in m.elements.items():
        cx = el._coords()[:, 0].mean()
        cy = el._coords()[:, 1].mean()
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            m.add_pressure(eid, p)
            elems_inside += 1

    header("CS06 - Piastra SS con carico parziale (patch load)")
    print(f"  L = {L} m, t = {t} m, E = {E:.2e} Pa, nu = {nu}, D = {D:.4e} N m")
    print(f"  Patch quadrata centrale: lato c = {c} m (c/L = {c / L})")
    print(f"  Elementi caricati: {elems_inside} / {len(m.elements)}")
    print()

    res = m.solve()
    w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)

    alpha_timoshenko = 0.00640
    w_ex = alpha_timoshenko * abs(p) * L ** 4 / D
    print(f"  w_max FEM (centro)        = {w_fem:.4e} m")
    print(f"  w_max Timoshenko (c/L=0.5) = {w_ex:.4e} m (alpha = {alpha_timoshenko})")
    print(f"  Errore indicativo: {abs(w_fem - w_ex) / w_ex * 100:.1f}%")
    print()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs06_mesh_{n_el}.png",
                title="Mesh con evidenziato il patch centrale")
    save_figure(plot_deformed(res, scale=200), f"cs06_deformed_{n_el}.png",
                title=f"Deformata con patch centrale (scala 200×)")
    save_figure(plot_contour(res, "w"), f"cs06_w_map_{n_el}.png",
                title="Spostamento w [m] — discontinuita' di gradiente al bordo del patch")
    save_figure(plot_contour(res, "Mx"), f"cs06_Mx_{n_el}.png",
                title="Mx [N·m/m]")
    save_figure(plot_contour(res, "My"), f"cs06_My_{n_el}.png",
                title="My [N·m/m]")
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
