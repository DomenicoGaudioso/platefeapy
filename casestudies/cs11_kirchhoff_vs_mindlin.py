"""Caso studio CS11: Confronto Kirchhoff (sottile) vs Mindlin (spesso).

Caso classico FEM. La teoria di Kirchhoff-Love e' valida per piastre sottili
(t/L < 1/20, tipicamente). La teoria di Mindlin-Reissner include la
deformabilita' a taglio trasversale e degenera correttamente in Kirchhoff
al tendere di L/t -> infinito (grazie all'integrazione ridotta selettiva
SRI che evita lo shear locking).

Questo caso studio mette a confronto le due teorie al variare del rapporto
di snellezza L/t, con un carico di pressione uniforme. Si dimostra che:
  * Per piastre snelle (L/t > 20), Kirchhoff e Mindlin danno risultati
    coincidenti a meno dell'1%.
  * Per piastre tozze (L/t < 5), Kirchhoff sottostima la cedevolezza,
    mentre Mindlin cattura correttamente il contributo di taglio.
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
    D_bending, header,
)


def build_plate(L: float, t: float, n_el: int, theory: str):
    m = Model()
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=t)
    rect_plate_mesh(m, L, L, n_el, n_el, mat, sec, theory=theory)
    build_ss_bc(m, axis="all")
    return m


def main() -> None:
    L = 1.0
    E, nu = 210e9, 0.3
    p = -1000.0
    D = D_bending(E, nu, 0.01)

    header("CS11 - Confronto Kirchhoff (thin) vs Mindlin (thick)")
    print(f"  L = {L} m, E = {E:.2e} Pa, nu = {nu}, p = {p} Pa")
    print(f"  Per t=0.01 m, D = {D:.4e} N m")
    print()
    print(f"  {'L/t':>6s}  {'t [m]':>10s}  {'mesh':>10s}  "
          f"{'w_Mindlin':>12s}  {'w_Kirchhoff':>12s}  {'diff %':>8s}")
    print("  " + "-" * 72)

    n_el = 16
    for L_over_t in [5, 10, 20, 50, 100, 200]:
        t = L / L_over_t
        m_mindlin = build_plate(L, t, n_el, theory="mindlin")
        for eid in m_mindlin.elements:
            m_mindlin.add_pressure(eid, p)
        res_m = m_mindlin.solve()
        w_m = max(abs(res_m.displacement(nid, "w")) for nid in m_mindlin.nodes)

        m_kirch = build_plate(L, t, n_el, theory="kirchhoff")
        for eid in m_kirch.elements:
            m_kirch.add_pressure(eid, p)
        res_k = m_kirch.solve()
        w_k = max(abs(res_k.displacement(nid, "w")) for nid in m_kirch.nodes)

        diff = abs(w_m - w_k) / max(abs(w_m), abs(w_k)) * 100
        print(f"  {L_over_t:>6d}  {t:>10.4f}  {n_el:>4d}x{n_el:<4d}  "
              f"{w_m:12.4e}  {w_k:12.4e}  {diff:7.3f}%")

    print()
    L_over_t = 5
    t = L / L_over_t
    m_mindlin = build_plate(L, t, n_el, theory="mindlin")
    for eid in m_mindlin.elements:
        m_mindlin.add_pressure(eid, p)
    res_m = m_mindlin.solve()

    m_kirch = build_plate(L, t, n_el, theory="kirchhoff")
    for eid in m_kirch.elements:
        m_kirch.add_pressure(eid, p)
    res_k = m_kirch.solve()

    save_figure(plot_mesh(m_mindlin, show_node_ids=False),
                f"cs11_mesh_{n_el}_t{t:.3f}.png",
                title=f"Mesh Mindlin, t = {t:.3f} m (L/t = {L_over_t})")
    save_figure(plot_deformed(res_m, scale=100), f"cs11_mindlin_deformed_t{t:.3f}.png",
                title=f"Deformata Mindlin, t = {t:.3f} m (L/t = {L_over_t})")
    save_figure(plot_contour(res_m, "w"), f"cs11_mindlin_w_t{t:.3f}.png",
                title="w Mindlin [m] — piastra tozza")
    save_figure(plot_contour(res_m, "Mx"), f"cs11_mindlin_Mx_t{t:.3f}.png",
                title="Mx Mindlin [N·m/m] — piastra tozza")
    print(f"  NB: la deformata Kirchhoff non e' visualizzabile con plot_deformed")
    print(f"      (interfaccia _shape_functions non esposta).")
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
