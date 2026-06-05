"""Caso studio CS05: Piastra rettangolare - influenza del rapporto di lato.

Caso classico (Timoshenko, "Theory of Plates and Shells", Cap. 3, p. 197).
Piastra rettangolare Lx x Ly, SS su tutti e quattro i lati, con pressione
uniforme p. Si varia il rapporto a/b = Lx/Ly mantenendo la stessa area e
materiale.

Per piastra rettangolare SS sotto UDL, Timoshenko fornisce il coefficiente
alpha(a/b) tale che:

    w_max = alpha(a/b) * p * a^4 / D

dove a = Lx e' il lato corto (per piastre allungate) e b = Ly il lato lungo.
Alcuni valori (Timoshenko Tab. 2, p. 196, nu=0.3):

    a/b     alpha
    1.0     0.00406
    0.8     0.00544
    0.667   0.00723
    0.5     0.01013
    0.4     0.01196
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


def alpha_timoshenko_ss_rect(ratio: float, nu: float = 0.3) -> float:
    """Coefficiente alpha(a/b) per piastra rettangolare SS sotto UDL.

    ratio = a/b, dove a e' il lato corto (<= b).
    Interpola dalla Tab. 2 di Timoshenko p.196 per nu=0.3.
    """
    table = {
        1.0: 0.00406, 0.9: 0.00467, 0.8: 0.00544, 0.7: 0.00630,
        0.667: 0.00723, 0.6: 0.00821, 0.5: 0.01013, 0.4: 0.01196,
        0.333: 0.01335, 0.25: 0.01416, 0.2: 0.01436,
    }
    rs = sorted(table.keys(), reverse=True)
    if ratio >= rs[0]:
        return table[rs[0]]
    if ratio <= rs[-1]:
        return table[rs[-1]]
    for k in range(len(rs) - 1):
        if rs[k + 1] <= ratio <= rs[k]:
            x0, x1 = rs[k], rs[k + 1]
            y0, y1 = table[x0], table[x1]
            return y0 + (y1 - y0) * (ratio - x0) / (x1 - x0)
    return table[rs[0]]


def main() -> None:
    E, nu, t = 210e9, 0.3, 0.01
    p = -1000.0
    D = D_bending(E, nu, t)
    b = 1.0

    header("CS05 - Piastra rettangolare: influenza rapporto lati")
    print(f"  E = {E:.2e} Pa, nu = {nu}, t = {t} m, p = {p} Pa")
    print(f"  D = {D:.4e} N m, lato lungo b = {b} m, lato corto a variabile")
    print()
    print(f"  {'a/b':>6s}  {'a':>5s}  {'mesh':>10s}  {'w_max FEM':>12s}  {'w_max esatto':>14s}  {'err %':>7s}")
    print("  " + "-" * 72)

    ratios = [1.0, 0.8, 0.667, 0.5, 0.4, 0.333]
    img_set = []
    for ratio in ratios:
        a = ratio * b
        n_ex = max(8, int(round(24 * a)))
        n_ey = max(8, int(round(24 * b)))
        m = Model()
        mat = Material(E=E, nu=nu)
        sec = ShellSection(t=t)
        rect_plate_mesh(m, a, b, n_ex, n_ey, mat, sec)
        build_ss_bc(m, axis="all")
        for eid in m.elements:
            m.add_pressure(eid, p)
        res = m.solve()
        w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
        alpha = alpha_timoshenko_ss_rect(ratio, nu)
        w_ex = alpha * abs(p) * a ** 4 / D
        err = abs(w_fem - w_ex) / w_ex * 100
        print(f"  {ratio:>6.3f}  {a:>5.3f}  {n_ex:>4d}x{n_ey:<4d}  {w_fem:12.4e}  {w_ex:14.4e}  {err:6.2f}%")
        img_set.append((ratio, a, m, res, w_fem, w_ex))

    print()
    for ratio, a, m, res, w_fem, w_ex in img_set:
        suffix = f"{ratio:.3f}".replace(".", "p")
        save_figure(plot_mesh(m, show_node_ids=False), f"cs05_mesh_{suffix}.png",
                    title=f"Mesh a/b = {ratio}")
        save_figure(plot_deformed(res, scale=200), f"cs05_deformed_{suffix}.png",
                    title=f"Deformata a/b = {ratio} (scala 200×)")
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
