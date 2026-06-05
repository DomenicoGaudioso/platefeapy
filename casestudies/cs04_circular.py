"""Caso studio CS04: piastra circolare con mesh mappata sul disco.

Riferimento classico: Timoshenko & Woinowsky-Krieger, "Theory of Plates and
Shells", formule per piastra circolare soggetta a pressione uniforme.

La mesh non nasce piu' da un rettangolo tagliato: ogni nodo della griglia
logica viene mappato direttamente sul disco con una trasformazione
quadrato-disco. Il bordo esterno e' quindi il cerchio discretizzato e non
rimangono elementi rettangolari esterni alla piastra.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from platefeapy import Material, Model, ShellSection
from platefeapy.plotting import (
    plot_contour, plot_deformed, plot_mesh, plot_reactions, plot_supports,
)

try:
    from .common import (
        D_bending,
        header,
        print_check,
        save_figure,
        timoshenko_circular_clamped_wmax,
        timoshenko_circular_ss_wmax,
    )
except ImportError:  # pragma: no cover - standalone execution
    from common import (
        D_bending,
        header,
        print_check,
        save_figure,
        timoshenko_circular_clamped_wmax,
        timoshenko_circular_ss_wmax,
    )


def _square_to_disk(a: float, b: float, R: float) -> tuple[float, float]:
    """Mappa concentrica di Shirley-Chiu da [-1,1]^2 al disco di raggio R."""
    if abs(a) < 1e-15 and abs(b) < 1e-15:
        return 0.0, 0.0
    if abs(a) > abs(b):
        r = a
        theta = (np.pi / 4.0) * (b / a)
    else:
        r = b
        theta = (np.pi / 2.0) - (np.pi / 4.0) * (a / b)
    return float(R * r * np.cos(theta)), float(R * r * np.sin(theta))


def build_circular_plate(R: float, n_el: int, bc: str, theory: str = "mindlin"):
    """Costruisce una piastra circolare Q4 mappata direttamente sul disco.

    bc: 'ss' oppure 'clamped'
    """
    if n_el < 4:
        raise ValueError("n_el deve essere almeno 4")

    m = Model()
    n = n_el + 1
    nid_grid: dict[tuple[int, int], int] = {}
    nid = 1
    for j in range(n):
        b = -1.0 + 2.0 * j / n_el
        for i in range(n):
            a = -1.0 + 2.0 * i / n_el
            x, y = _square_to_disk(a, b, R)
            m.add_node(nid, x, y)
            nid_grid[(i, j)] = nid
            nid += 1

    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)

    eid = 1
    for j in range(n_el):
        for i in range(n_el):
            m.add_plate(
                eid,
                [
                    nid_grid[(i, j)],
                    nid_grid[(i + 1, j)],
                    nid_grid[(i + 1, j + 1)],
                    nid_grid[(i, j + 1)],
                ],
                mat,
                sec,
                theory=theory,
            )
            eid += 1

    boundary_ids = {
        node_id
        for (i, j), node_id in nid_grid.items()
        if i in (0, n_el) or j in (0, n_el)
    }
    for node_id in boundary_ids:
        if bc == "ss":
            m.fix(node_id, ["w"])
        elif bc == "clamped":
            m.fix(node_id)
        else:
            raise ValueError("bc deve essere 'ss' oppure 'clamped'")

    return m, list(m.elements), list(m.nodes), sorted(boundary_ids)


def main() -> None:
    R = 1.0
    p = -1000.0
    E, nu, t = 210e9, 0.3, 0.01
    D = D_bending(E, nu, t)

    header("CS04 - Piastra circolare con mesh mappata")
    print(f"  R = {R} m, t = {t} m, p = {p} Pa, E = {E:.2e} Pa, nu = {nu}")
    print(f"  D = {D:.4e} N m")
    print("  Mesh: Q4 mappata sul disco, senza rettangolo esterno")
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
            m, elems, node_ids, _ = build_circular_plate(R, n_el, bc=bc)
            for eid in elems:
                m.add_pressure(eid, p)
            res = m.solve()
            w_fem = max(abs(res.displacement(nid, "w")) for nid in node_ids)
            err = abs(w_fem - w_ex) / w_ex * 100
            print(f"  {n_el:>4d}x{n_el:<4d}  {w_fem:12.4e}  {err:7.3f}%")
        print()

    bc = "ss"
    n_el = 32
    m, elems, node_ids, _ = build_circular_plate(R, n_el, bc=bc)
    for eid in elems:
        m.add_pressure(eid, p)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs04_mesh_{bc}_{n_el}.png")
    save_figure(plot_supports(m), f"cs04_supports_{bc}_{n_el}.png",
                title="Vincoli piastra circolare SS")
    save_figure(plot_deformed(res, scale=400), f"cs04_deformed_{bc}_{n_el}.png",
                title="Deformata circolare SS (scala 400x)")
    save_figure(plot_contour(res, "w"), f"cs04_w_map_{bc}_{n_el}.png",
                title="Spostamento w [m] (vista piana)")
    save_figure(plot_contour(res, "Mx"), f"cs04_Mx_{bc}_{n_el}.png",
                title="Mx [N m/m]")
    save_figure(plot_contour(res, "My"), f"cs04_My_{bc}_{n_el}.png",
                title="My [N m/m]")
    save_figure(plot_reactions(res), f"cs04_reactions_{bc}_{n_el}.png",
                title="Reazioni vincolari piastra circolare SS")

    w_fem = max(abs(res.displacement(nid, "w")) for nid in node_ids)
    w_ex = timoshenko_circular_ss_wmax(p, R, E, nu, t)
    print_check("w_max al centro (SS)", w_fem, w_ex, tol=0.10)
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
