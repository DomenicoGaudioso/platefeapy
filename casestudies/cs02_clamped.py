"""Caso studio CS02: Piastra quadrata incastrata - Timoshenko.

Caso classico (Timoshenko, "Theory of Plates and Shells", Cap. 3, p. 197).
Piastra quadrata di lato L incastrata su tutto il perimetro, soggetta a
pressione uniforme p.

Soluzione analitica (Timoshenko & Woinowsky-Krieger):

    w_max = 0.00126 * p * L^4 / D

dove D = E t^3 / (12 (1 - nu^2)).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from platefeapy import Model, Material, ShellSection
from platefeapy.plotting import plot_mesh, plot_deformed, plot_contour

from common import (
    rect_plate_mesh, build_clamped_bc, save_figure,
    timoshenko_clamped_wmax, D_bending, print_check, header,
)


def build_model(L: float, n_el: int, theory: str = "mindlin"):
    m = Model()
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    rect_plate_mesh(m, L, L, n_el, n_el, mat, sec, theory=theory)
    build_clamped_bc(m)
    return m


def main() -> None:
    L = 1.0
    p = -1000.0
    E, nu, t = 210e9, 0.3, 0.01
    D = D_bending(E, nu, t)
    w_exact = timoshenko_clamped_wmax(p, L, E, nu, t)

    header("CS02 - Piastra incastrata: convergenza mesh")
    print(f"  L = {L} m, t = {t} m, p = {p} Pa, E = {E:.2e} Pa, nu = {nu}")
    print(f"  D = {D:.4e} N m")
    print(f"  w_max esatto (Timoshenko) = {w_exact:.6e} m")
    print()
    print(f"  {'mesh':>10s}  {'w_max FEM [m]':>16s}  {'err %':>8s}")
    print("  " + "-" * 42)

    for n_el in (4, 8, 12, 16, 20):
        m = build_model(L, n_el, theory="mindlin")
        for eid in m.elements:
            m.add_pressure(eid, p)
        res = m.solve()
        w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
        err = abs(w_fem - w_exact) / w_exact * 100
        print(f"  {n_el:>4d}x{n_el:<4d}  {w_fem:16.6e}  {err:7.3f}%")

    print()
    n_el = 16
    m = build_model(L, n_el, theory="mindlin")
    for eid in m.elements:
        m.add_pressure(eid, p)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs02_mesh_{n_el}.png")
    save_figure(plot_deformed(res, scale=400), f"cs02_deformed_{n_el}.png",
                title=f"Deformata incastrata (scala 400×), w_max = {w_exact:.3e} m")
    save_figure(plot_contour(res, "w"), f"cs02_w_map_{n_el}.png",
                title="Spostamento w [m]")
    save_figure(plot_contour(res, "Mx"), f"cs02_Mx_{n_el}.png",
                title="Mx incastrata: massimi agli spigoli [N·m/m]")
    save_figure(plot_contour(res, "Mxy"), f"cs02_Mxy_{n_el}.png",
                title="Mxy incastrata: concentrazioni agli spigoli [N·m/m]")
    save_figure(plot_contour(res, "Qx"), f"cs02_Qx_{n_el}.png",
                title="Taglio Qx [N/m]")
    save_figure(plot_contour(res, "Qy"), f"cs02_Qy_{n_el}.png",
                title="Taglio Qy [N/m]")

    w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
    print_check("w_max al centro", w_fem, w_exact, tol=0.02)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
