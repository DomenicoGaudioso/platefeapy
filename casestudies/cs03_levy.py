"""Caso studio CS03: Piastra Levy (2 lati SS, 2 lati liberi) - Timoshenko.

Caso classico (Timoshenko, "Theory of Plates and Shells", Tab. 3, p. 197).
Piastra rettangolare con due lati opposti (y=0 e y=b) semplicemente appoggiati
e i restanti due (x=0 e x=a) liberi, soggetta a pressione uniforme p.

Soluzione analitica (Levy, serie semplice di seni in direzione y):

    w(x,y) = sum_m A_m * sinh(alpha_m (a-x)/b) * sin(m pi y / b)
            con alpha_m = m pi a / b

Il coefficiente w_max * D / (p a^4) dipende dal rapporto a/b e da nu.

Per piastra quadrata (a = b) e nu = 0.3, Timoshenko fornisce:

    w_max = 0.00504 * p * a^4 / D

Per rapporti a/b diversi si interpola dalla tabella di Timoshenko (vedi
funzione levy_wmax in common.py).
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
    levy_wmax, D_bending, print_check, header,
)


def build_levy_model(a: float, b: float, n_ex: int, n_ey: int, theory: str = "mindlin"):
    """Piastra Levy: lati y=0 e y=b appoggiati, lati x=0 e x=a liberi."""
    m = Model()
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    rect_plate_mesh(m, a, b, n_ex, n_ey, mat, sec, theory=theory)
    build_ss_bc(m, axis="y")
    return m


def main() -> None:
    E, nu, t = 210e9, 0.3, 0.01
    p = -1000.0
    D = D_bending(E, nu, t)

    header("CS03 - Piastra Levy (2 lati SS, 2 lati liberi)")
    print(f"  E = {E:.2e} Pa, nu = {nu}, t = {t} m, p = {p} Pa")
    print(f"  D = {D:.4e} N m")
    print()

    cases = [
        ("Quadrata a=b=1.0", 1.0, 1.0, 0.00504, 20, 20),
        ("Allungata a=1.5, b=1.0", 1.5, 1.0, 0.00257, 30, 20),
        ("Allungata a=2.0, b=1.0", 2.0, 1.0, 0.00144, 40, 20),
        ("Larga    a=1.0, b=1.5", 1.0, 1.5, None, 20, 30),
        ("Larga    a=1.0, b=2.0", 1.0, 2.0, None, 20, 40),
    ]

    print(f"  {'caso':<30s} {'a':>5s}  {'b':>5s}  {'w_max FEM':>12s}  {'w_max esatto':>14s}  {'err %':>7s}")
    print("  " + "-" * 80)

    for label, a, b, alpha, nex, ney in cases:
        if "Larga" in label:
            continue
        m = build_levy_model(a, b, nex, ney)
        for eid in m.elements:
            m.add_pressure(eid, p)
        res = m.solve()
        w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
        w_ex = levy_wmax(a, b, p, E, nu, t) if alpha is not None else None
        if w_ex is not None:
            err = abs(w_fem - w_ex) / w_ex * 100
            print(f"  {label:<30s} {a:>5.2f}  {b:>5.2f}  {w_fem:12.4e}  {w_ex:14.4e}  {err:6.2f}%")
        else:
            print(f"  {label:<30s} {a:>5.2f}  {b:>5.2f}  {w_fem:12.4e}  {'(non in tab.)':>14s}")

    print()
    a, b, nex, ney = 1.0, 1.0, 20, 20
    m = build_levy_model(a, b, nex, ney)
    for eid in m.elements:
        m.add_pressure(eid, p)
    res = m.solve()
    w_ex = levy_wmax(a, b, p, E, nu, t)
    save_figure(plot_mesh(m, show_node_ids=False), "cs03_mesh.png")
    save_figure(plot_deformed(res, scale=200), "cs03_deformed.png",
                title="Deformata Levy quadrata (scala 200×)")
    save_figure(plot_contour(res, "w"), "cs03_w_map.png",
                title="Spostamento w [m]")
    save_figure(plot_contour(res, "Mx"), "cs03_Mx.png",
                title="Mx [N·m/m]")
    save_figure(plot_contour(res, "My"), "cs03_My.png",
                title="My [N·m/m]")

    w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
    print_check("w_max Levy quadrata", w_fem, w_ex, tol=0.05)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
