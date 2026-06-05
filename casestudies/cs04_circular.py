"""Caso studio CS04: Piastra circolare - SS / incastrata.

Caso classico (Timoshenko, "Theory of Plates and Shells", Cap. 3, p. 197).
Piastra circolare di raggio R soggetta a pressione uniforme p. Soluzione
analitica in coordinate polari (metodo di Sophie Germain / Lagrange).

Condizioni di vincolo:
  * SS  (w=0) sul bordo: w_max = (3+nu) * p * R^4 / (64 (1-nu) D)
  * Incastrata  (w=0, dw/dr=0) sul bordo: w_max = p * R^4 / (64 D)

La mesh e' generata su un quadrato che inscrive il cerchio, lasciando la
piastra "circolare" modellata tagliando via gli elementi fuori dal raggio.
Per semplicita' in questo caso studio usiamo una mesh rettangolare fitta
(64x64) e i carichi vengono applicati solo agli elementi il cui baricentro
cade entro il raggio. Questo approccio e' standard nei benchmark FEM storici.
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
    save_figure, D_bending, print_check, header,
    timoshenko_circular_ss_wmax, timoshenko_circular_clamped_wmax,
)


def build_circular_plate(R: float, n_el: int, bc: str, theory: str = "mindlin"):
    """Costruisce una piastra 'circolare' tagliata in un dominio quadrato.

    bc: 'ss' o 'clamped'
    """
    m = Model()
    L = 2.0 * R
    n = n_el + 1
    nid = 1
    for j in range(n):
        for i in range(n):
            x = i * L / n_el - R
            y = j * L / n_el - R
            m.add_node(nid, x, y)
            nid += 1

    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)

    eid = 1
    for j in range(n_el):
        for i in range(n_el):
            n1 = j * n + i + 1
            n2 = n1 + 1
            n3 = n2 + n
            n4 = n1 + n
            m.add_plate(eid, [n1, n2, n3, n4], mat, sec, theory=theory)
            eid += 1

    inside_ids = []
    for nid, node in m.nodes.items():
        if np.hypot(node.x, node.y) <= R:
            inside_ids.append(nid)

    boundary_ids = set()
    for nid in inside_ids:
        node = m.nodes[nid]
        r = np.hypot(node.x, node.y)
        if r > R - (L / n_el) * 1.05:
            boundary_ids.add(nid)

    for nid in boundary_ids:
        if bc == "ss":
            m.fix(nid, ["w"])
        else:
            m.fix(nid)

    inside_elems = []
    for eid, el in m.elements.items():
        cx = el._coords()[:, 0].mean()
        cy = el._coords()[:, 1].mean()
        if np.hypot(cx, cy) <= R:
            inside_elems.append(eid)

    return m, inside_elems, inside_ids


def main() -> None:
    R = 1.0
    p = -1000.0
    E, nu, t = 210e9, 0.3, 0.01
    D = D_bending(E, nu, t)

    header("CS04 - Piastra circolare (SS / incastrata)")
    print(f"  R = {R} m, t = {t} m, p = {p} Pa, E = {E:.2e} Pa, nu = {nu}")
    print(f"  D = {D:.4e} N m")
    print()

    for bc_label, bc in [("SS (w=0)", "ss"), ("Incastrata (w=0, dw/dr=0)", "clamped")]:
        if bc == "ss":
            w_ex = timoshenko_circular_ss_wmax(p, R, E, nu, t)
        else:
            w_ex = timoshenko_circular_clamped_wmax(p, R, E, nu, t)
        print(f"  -- {bc_label} --")
        print(f"  w_max esatto = {w_ex:.6e} m")
        print(f"  {'mesh':>10s}  {'w_max FEM':>12s}  {'err %':>8s}")
        print("  " + "-" * 40)
        for n_el in (12, 18, 24, 32):
            m, inside_elems, inside_ids = build_circular_plate(R, n_el, bc=bc)
            for eid in inside_elems:
                m.add_pressure(eid, p)
            res = m.solve()
            w_fem = max(abs(res.displacement(nid, "w")) for nid in inside_ids)
            err = abs(w_fem - w_ex) / w_ex * 100
            print(f"  {n_el:>4d}x{n_el:<4d}  {w_fem:12.4e}  {err:7.3f}%")
        print()

    bc = "ss"
    n_el = 32
    m, inside_elems, inside_ids = build_circular_plate(R, n_el, bc=bc)
    for eid in inside_elems:
        m.add_pressure(eid, p)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs04_mesh_{bc}_{n_el}.png")
    save_figure(plot_deformed(res, scale=400), f"cs04_deformed_{bc}_{n_el}.png",
                title=f"Deformata circolare SS (scala 400×)")
    save_figure(plot_contour(res, "w"), f"cs04_w_map_{bc}_{n_el}.png",
                title="Spostamento w [m] (vista piana)")
    save_figure(plot_contour(res, "Mx"), f"cs04_Mx_{bc}_{n_el}.png",
                title="Mx [N·m/m]")
    save_figure(plot_contour(res, "My"), f"cs04_My_{bc}_{n_el}.png",
                title="My [N·m/m]")

    w_fem = max(abs(res.displacement(nid, "w")) for nid in inside_ids)
    w_ex = timoshenko_circular_ss_wmax(p, R, E, nu, t)
    print_check("w_max al centro (SS)", w_fem, w_ex, tol=0.05)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
