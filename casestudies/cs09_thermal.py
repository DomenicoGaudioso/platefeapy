"""Caso studio CS09: Piastra con gradiente termico attraverso lo spessore.

Caso classico FEM. Una piastra rettangolare, vincolata in modo isostatico,
e' soggetta a un gradiente termico lineare dT attraverso lo spessore. Tale
gradiente induce una curvatura termica:

    kappa_th = alpha * dT / t

con alpha coefficiente di dilatazione termica. Il momento termico equivalente
vale (Kirchhoff / Mindlin thin):

    M_th = D * (1 + nu) * kappa_th

In questo caso studio:
  * Piastra quadrata 1x1 m, spessore t = 0.01 m
  * Vincoli: SS (w=0) lungo tutti i bordi
  * Materiale: acciaio (E = 210 GPa, nu = 0.3, alpha = 1.2e-5 /K)
  * Gradiente termico: dT = 100 K (faccia superiore +100 K rispetto all'inferiore)

Verifica: la freccia indotta dal gradiente puro (in assenza di carichi
meccanici) deve essere confrontabile con quella di una curvatura imposta.
Per piastra SS, la curvatura termica uniforme genera un momento costante
M = D*(1+nu)*kappa_th che induce un w_max confrontabile con:

    w_max ≈ (5/384) * M_th * L^2 / D  (per trave semplificata)
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
    D_bending, header,
)


def main() -> None:
    L = 1.0
    E, nu, t = 210e9, 0.3, 0.01
    alpha_th = 1.2e-5
    dT = 100.0
    D = D_bending(E, nu, t)
    kappa_th = alpha_th * dT / t
    M_th = D * (1.0 + nu) * kappa_th

    header("CS09 - Piastra con gradiente termico di spessore")
    print(f"  L = {L} m, t = {t} m, E = {E:.2e} Pa, nu = {nu}")
    print(f"  alpha = {alpha_th:.2e} /K, dT = {dT} K")
    print(f"  D = {D:.4e} N m")
    print(f"  kappa_th = alpha*dT/t = {kappa_th:.4e} 1/m")
    print(f"  M_th = D*(1+nu)*kappa_th = {M_th:.4e} N m/m")
    print()

    n_el = 16
    m = Model()
    mat = Material(E=E, nu=nu, alpha=alpha_th)
    sec = ShellSection(t=t)
    rect_plate_mesh(m, L, L, n_el, n_el, mat, sec)
    build_ss_bc(m, axis="all")
    for eid in m.elements:
        m.add_thermal_load(eid, dT)

    res = m.solve()
    w_fem = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
    print(f"  w_max al centro (dovuta al gradiente) = {w_fem:.4e} m")
    print()

    w_simple_beam = (5.0 / 384.0) * abs(M_th) * L ** 2 / D
    print(f"  Confronto semplificato 'trave' 5*M*L^2/(384 D) = {w_simple_beam:.4e} m")
    print(f"  (ordine di grandezza indicativo, la piastra e' un sistema 2D)")
    print()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs09_mesh_{n_el}.png",
                title="Mesh con gradiente termico di spessore")
    save_figure(plot_deformed(res, scale=200), f"cs09_deformed_{n_el}.png",
                title=f"Curvatura termica dT = {dT} K (scala 200×)")
    save_figure(plot_contour(res, "w"), f"cs09_w_map_{n_el}.png",
                title="Spostamento w [m]")
    save_figure(plot_contour(res, "Mx"), f"cs09_Mx_{n_el}.png",
                title="Mx [N·m/m] — momento termico")
    save_figure(plot_contour(res, "My"), f"cs09_My_{n_el}.png",
                title="My [N·m/m]")
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
