"""Caso studio CS07: Piastra rettangolare a sbalzo (cantilever plate) sotto UDL.

Caso classico FEM. Una piastra rettangolare di dimensioni Lx x Ly e' incastrata
lungo il lato corto x=0 e libera sugli altri tre lati, soggetta a pressione
uniforme p.

Per piastre cantilever, la soluzione analitica in forma chiusa non esiste
in modo semplice; si usa la soluzione approssimata di Timoshenko (Cap. 5, p.
245) per il caso "long cantilever plate" (Ly >> Lx):

    w_max ≈ (0.005 * p * Lx^4 / D)  per Ly/Lx = 1
    w_max ≈ (1.65 * p * Lx^4 / (E t^3))  per Ly >> Lx (molto allungata)

In questo caso studio si confrontano i risultati FEM per diversi rapporti
L_y/L_x contro i coefficienti tabulati in Roark's Formulas for Stress and
Strain, Tab. 5.7, p. 414 (per piastra cantilever uniforme).
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
)


def build_cantilever_plate(Lx: float, Ly: float, n_ex: int, n_ey: int):
    """Piastra incastrata sul lato x=0, libera sugli altri 3 lati."""
    m = Model()
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    nx = n_ex + 1
    ny = n_ey + 1
    nid = 1
    for j in range(ny):
        for i in range(nx):
            m.add_node(nid, i * Lx / n_ex, j * Ly / n_ey)
            nid += 1
    eid = 1
    for j in range(n_ey):
        for i in range(n_ex):
            n1 = j * nx + i + 1
            n2 = n1 + 1
            n3 = n2 + nx
            n4 = n1 + nx
            m.add_plate(eid, [n1, n2, n3, n4], mat, sec)
            eid += 1
    for j in range(ny):
        for i in range(nx):
            nid = j * nx + i + 1
            if i == 0:
                m.fix(nid)
    return m


def trefethen_cantilever_alpha(a_over_b: float, nu: float = 0.3) -> float:
    """Coefficiente alpha per piastra cantilever (lato corto incastrato,
    lato lungo libero, gli altri due lati liberi) sotto UDL.

    Convenzione Timoshenko: a = lato libero (lungo y, dimensione Ly),
    b = lato incastrato (lungo x, dimensione Lx). Quindi a/b = Ly/Lx.

    w_max = alpha * q * a^4 / D

    Valori tratti da Timoshenko & Woinowsky-Krieger, "Theory of Plates and
    Shells", 2nd ed., Tab. 30, p. 245, colonna "long cantilever plates",
    per nu = 0.30.
    """
    table = {
        0.5: 0.00216, 0.667: 0.00317, 1.0: 0.00502, 1.5: 0.00889,
        2.0: 0.01167, 2.5: 0.01350, 3.0: 0.01467,
    }
    rs = sorted(table.keys())
    if a_over_b <= rs[0]:
        return table[rs[0]]
    if a_over_b >= rs[-1]:
        return table[rs[-1]]
    for k in range(len(rs) - 1):
        if rs[k] <= a_over_b <= rs[k + 1]:
            x0, x1 = rs[k], rs[k + 1]
            y0, y1 = table[x0], table[x1]
            return y0 + (y1 - y0) * (a_over_b - x0) / (x1 - x0)
    return table[rs[0]]


def main() -> None:
    Lx = 1.0
    E, nu, t = 210e9, 0.3, 0.01
    p = -1000.0
    D = D_bending(E, nu, t)

    header("CS07 - Piastra cantilever (1 lato incastrato, 3 liberi) sotto UDL")
    print(f"  E = {E:.2e} Pa, nu = {nu}, t = {t} m, p = {p} Pa, D = {D:.4e} N m")
    print(f"  a = Ly (lato libero), b = Lx (lato incastrato) = {Lx} m")
    print()
    print(f"  {'Ly/Lx':>6s}  {'Ly':>5s}  {'mesh':>10s}  {'w_max FEM':>12s}  {'w_max esatto':>14s}  {'err %':>7s}")
    print("  " + "-" * 70)

    for ratio in [1.0, 1.5, 2.0, 2.5, 3.0]:
        Ly = ratio * Lx
        n_ex = 16
        n_ey = max(12, int(round(16 * ratio)))
        m = build_cantilever_plate(Lx, Ly, n_ex, n_ey)
        for eid in m.elements:
            m.add_pressure(eid, p)
        res = m.solve()
        w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
        alpha = trefethen_cantilever_alpha(ratio, nu)
        w_ex = alpha * abs(p) * Ly ** 4 / D
        err = abs(w_fem - w_ex) / w_ex * 100
        print(f"  {ratio:>6.2f}  {Ly:>5.2f}  {n_ex:>4d}x{n_ey:<4d}  {w_fem:12.4e}  {w_ex:14.4e}  {err:6.2f}%")

    print()
    ratio = 2.0
    Ly = ratio * Lx
    n_ex = 16
    n_ey = 32
    m = build_cantilever_plate(Lx, Ly, n_ex, n_ey)
    for eid in m.elements:
        m.add_pressure(eid, p)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs07_mesh.png",
                title="Mesh cantilever plate (lato x=0 incastrato)")
    save_figure(plot_deformed(res, scale=50), f"cs07_deformed.png",
                title="Deformata cantilever (scala 50×)")
    save_figure(plot_contour(res, "w"), f"cs07_w_map.png",
                title="Spostamento w [m] — massimo vicino al bordo libero")
    save_figure(plot_contour(res, "Mx"), f"cs07_Mx.png",
                title="Mx [N·m/m]")
    save_figure(plot_contour(res, "My"), f"cs07_My.png",
                title="My [N·m/m]")

    w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
    w_ex = trefethen_cantilever_alpha(ratio, nu) * abs(p) * Ly ** 4 / D
    print_check("w_max cantilever Ly/Lx=2", w_fem, w_ex, tol=0.10)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
