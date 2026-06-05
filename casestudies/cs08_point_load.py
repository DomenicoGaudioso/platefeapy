"""Caso studio CS08: Carico concentrato in centro piastra SS.

Caso classico (Timoshenko, "Theory of Plates and Shells", Cap. 3, p. 124,
Tab. 4). Piastra quadrata SS di lato L soggetta a una forza concentrata P
applicata al centro.

Soluzione approssimata (Timoshenko):

    w_max(centro) = 0.01160 * P * L^2 / D

(coefficiente per piastra SS quadrata, carico centrale concentrato, nu=0.3).

In realta', per il confronto FEM, il carico "concentrato" viene applicato
distribuendolo sui 4 nodi piu' vicini al centro (in realta' sui 4 elementi
adiacenti, ovvero 9 nodi centrali con pesi di quadratura 1/4 ciascuno se
l'area di applicazione e' uguale all'area di un elemento centrale, o in
modo equivalente applicato come forza nodale diretta).
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
    P = -1000.0
    D = D_bending(E, nu, t)
    w_ex = 0.01160 * abs(P) * L ** 2 / D

    header("CS08 - Piastra SS con carico concentrato al centro")
    print(f"  L = {L} m, t = {t} m, P = {P} N, E = {E:.2e} Pa, nu = {nu}")
    print(f"  D = {D:.4e} N m")
    print(f"  w_max esatto (Timoshenko) = {w_ex:.6e} m")
    print()
    print(f"  {'mesh':>10s}  {'w_max FEM':>14s}  {'err %':>8s}")
    print("  " + "-" * 38)

    for n_el in (8, 16, 24, 32):
        m = Model()
        mat = Material(E=E, nu=nu)
        sec = ShellSection(t=t)
        rect_plate_mesh(m, L, L, n_el, n_el, mat, sec)
        build_ss_bc(m, axis="all")

        cx_idx = n_el // 2
        cy_idx = n_el // 2
        center_nid = cy_idx * (n_el + 1) + cx_idx + 1
        m.add_nodal_load(center_nid, Fz=P)

        res = m.solve()
        w_fem = abs(res.displacement(center_nid, "w"))
        err = abs(w_fem - w_ex) / w_ex * 100
        print(f"  {n_el:>4d}x{n_el:<4d}  {w_fem:14.4e}  {err:7.3f}%")

    print()
    n_el = 32
    m = Model()
    mat = Material(E=E, nu=nu)
    sec = ShellSection(t=t)
    rect_plate_mesh(m, L, L, n_el, n_el, mat, sec)
    build_ss_bc(m, axis="all")
    cx_idx = n_el // 2
    cy_idx = n_el // 2
    center_nid = cy_idx * (n_el + 1) + cx_idx + 1
    m.add_nodal_load(center_nid, Fz=P)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs08_mesh_{n_el}.png")
    save_figure(plot_deformed(res, scale=200), f"cs08_deformed_{n_el}.png",
                title=f"Deformata per carico P={P} N al centro (scala 200×)")
    save_figure(plot_contour(res, "w"), f"cs08_w_map_{n_el}.png",
                title="w [m] — picco al centro")
    save_figure(plot_contour(res, "Mx"), f"cs08_Mx_{n_el}.png",
                title="Mx [N·m/m] — concentrazione al punto di carico")
    save_figure(plot_contour(res, "Mxy"), f"cs08_Mxy_{n_el}.png",
                title="Mxy [N·m/m]")

    w_fem = abs(res.displacement(center_nid, "w"))
    print_check("w_max al centro", w_fem, w_ex, tol=0.20)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
