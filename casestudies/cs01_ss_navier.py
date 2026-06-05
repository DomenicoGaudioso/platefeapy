"""Caso studio CS01: Piastra quadrata semplicemente appoggiata - Navier.

Caso classico della letteratura FEM (Timoshenko, "Theory of Plates and Shells",
Cap. 3, §3, p. 197). Piastra quadrata di lato L, vincolata con appoggio
semplice su tutti e quattro i lati, soggetta a pressione uniforme p.

Soluzione analitica (Navier, serie doppia di seni):

    w(x,y) = sum_m sum_n  (4 p / (pi^6 D)) * (sin(m pi x/L) sin(n pi y/L))
                                 / (m n (m^2/L^2 + n^2/L^2)^2)

Al centro della piastra (x = y = L/2), il coefficiente per piastra quadrata
(Lx = Ly = L) con pressione uniforme vale:

    w_max = 0.00406 * p * L^4 / D

dove D = E t^3 / (12 (1 - nu^2)) e' la rigidezza flessionale.

Output:
- mesh.png, deformed.png, Mx.png, My.png, w_map.png
- tabella di convergenza vs soluzione esatta.
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
    navier_ss_wmax, D_bending, print_check, header,
)


def build_model(L: float, n_el: int, theory: str = "mindlin"):
    m = Model()
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    rect_plate_mesh(m, L, L, n_el, n_el, mat, sec, theory=theory)
    build_ss_bc(m, axis="all")
    return m


def main() -> None:
    L = 1.0
    p = -1000.0
    E, nu, t = 210e9, 0.3, 0.01
    D = D_bending(E, nu, t)
    w_exact = navier_ss_wmax(p, L, E, nu, t)

    header("CS01 - Piastra SS Navier: convergenza mesh")
    print(f"  L = {L} m, t = {t} m, p = {p} Pa, E = {E:.2e} Pa, nu = {nu}")
    print(f"  D = {D:.4e} N m")
    print(f"  w_max esatto (Navier) = {w_exact:.6e} m")
    print()
    print(f"  {'mesh':>10s}  {'w_max FEM [m]':>16s}  {'err %':>8s}")
    print("  " + "-" * 42)

    results = []
    for n_el in (4, 8, 12, 16, 20):
        m = build_model(L, n_el, theory="mindlin")
        for eid in m.elements:
            m.add_pressure(eid, p)
        res = m.solve()
        w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
        err = abs(w_fem - w_exact) / w_exact * 100
        results.append((n_el, w_fem, err))
        print(f"  {n_el:>4d}x{n_el:<4d}  {w_fem:16.6e}  {err:7.3f}%")

    print()

    n_el = 16
    m = build_model(L, n_el, theory="mindlin")
    for eid in m.elements:
        m.add_pressure(eid, p)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs01_mesh_{n_el}.png")
    save_figure(plot_deformed(res, scale=200), f"cs01_deformed_{n_el}.png",
                title=f"Deformata SS Navier (scala 200×), w_max = {w_exact:.3e} m")
    save_figure(plot_contour(res, "w"), f"cs01_w_map_{n_el}.png",
                title="Spostamento trasversale w [m]")
    save_figure(plot_contour(res, "Mx"), f"cs01_Mx_{n_el}.png",
                title="Momento flettente Mx [N·m/m]")
    save_figure(plot_contour(res, "My"), f"cs01_My_{n_el}.png",
                title="Momento flettente My [N·m/m]")
    save_figure(plot_contour(res, "Mxy"), f"cs01_Mxy_{n_el}.png",
                title="Momento torcente Mxy [N·m/m]")

    w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
    print_check("w_max al centro", w_fem, w_exact, tol=0.02)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
