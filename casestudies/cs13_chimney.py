"""Caso studio CS13: sviluppo piano di una ciminiera cilindrica sottile.

Il modello rappresenta lo sviluppo equivalente della parete di una ciminiera
in c.a. rastremata, con apertura di servizio alla base e pressione da vento
variabile in altezza. E' un caso dimostrativo per mesh Q4 generiche: il dominio
non e' rettangolare, contiene un foro e mantiene il fusto con larghezza
circonferenziale variabile.

Riferimenti ingegneristici usati come impostazione qualitativa:
- ACI 307-23, Requirements for Reinforced Concrete Chimneys.
- CICIND Model Code for Concrete Chimneys, Part A - The Shell.
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
    from .common import header, print_check, save_figure
except ImportError:  # pragma: no cover - standalone execution
    from common import header, print_check, save_figure


def radius_at_height(z: float, H: float, r_base: float, r_top: float) -> float:
    return r_base + (r_top - r_base) * z / H


def _node_xy(theta: float, z: float, H: float, r_base: float, r_top: float):
    r = radius_at_height(z, H, r_base, r_top)
    return theta * r, z


def _inside_service_opening(x: float, z: float) -> bool:
    return abs(x) < 1.45 and 3.0 < z < 12.0


def build_chimney_wall(nx: int = 20, nz: int = 32, theory: str = "mindlin"):
    """Costruisce lo sviluppo piano di una ciminiera rastremata con foro."""
    H = 60.0
    r_base = 3.0
    r_top = 2.05
    mat = Material(E=30e9, nu=0.20)
    sec = ShellSection(t=0.40)

    theta_vals = np.linspace(-np.pi, np.pi, nx + 1)
    z_vals = np.linspace(0.0, H, nz + 1)

    kept_cells: list[tuple[int, int]] = []
    used_grid_nodes: set[tuple[int, int]] = set()
    for j in range(nz):
        for i in range(nx):
            theta_c = 0.5 * (theta_vals[i] + theta_vals[i + 1])
            z_c = 0.5 * (z_vals[j] + z_vals[j + 1])
            x_c, _ = _node_xy(theta_c, z_c, H, r_base, r_top)
            if _inside_service_opening(x_c, z_c):
                continue
            kept_cells.append((i, j))
            used_grid_nodes.update({
                (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1),
            })

    m = Model()
    node_map: dict[tuple[int, int], int] = {}
    for nid, key in enumerate(sorted(used_grid_nodes, key=lambda p: (p[1], p[0])), start=1):
        i, j = key
        x, y = _node_xy(theta_vals[i], z_vals[j], H, r_base, r_top)
        m.add_node(nid, x, y)
        node_map[key] = nid

    eid = 1
    elem_theta_z: dict[int, tuple[float, float]] = {}
    for i, j in kept_cells:
        nodes = [
            node_map[(i, j)],
            node_map[(i + 1, j)],
            node_map[(i + 1, j + 1)],
            node_map[(i, j + 1)],
        ]
        m.add_plate(eid, nodes, mat, sec, theory=theory)
        elem_theta_z[eid] = (
            0.5 * (theta_vals[i] + theta_vals[i + 1]),
            0.5 * (z_vals[j] + z_vals[j + 1]),
        )
        eid += 1

    base_nodes = [
        nid for (i, j), nid in node_map.items()
        if j == 0
    ]
    for nid in base_nodes:
        m.fix(nid)

    return m, elem_theta_z, {
        "H": H,
        "r_base": r_base,
        "r_top": r_top,
        "thickness": sec.t,
        "base_nodes": base_nodes,
    }


def wind_pressure(theta: float, z: float, H: float) -> float:
    """Pressione radiale equivalente: quota crescente e massimo sul lato vento."""
    q_top = 500.0
    q_z = q_top * (0.35 + 0.65 * (z / H) ** 0.25)
    cp = max(0.0, np.cos(theta)) + 0.18 * max(0.0, -np.cos(theta))
    return -q_z * cp


def main() -> None:
    m, elem_theta_z, meta = build_chimney_wall()
    H = meta["H"]
    for eid, (theta, z) in elem_theta_z.items():
        m.add_pressure(eid, wind_pressure(theta, z, H))

    res = m.solve()
    max_w = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
    total_reaction = sum(res.reactions(nid)[0] for nid in meta["base_nodes"])
    total_load = float(m.assemble_loads()[0::3].sum())

    header("CS13 - Ciminiera rastremata con apertura di servizio")
    print(f"  H = {H:.1f} m, r_base = {meta['r_base']:.2f} m, r_top = {meta['r_top']:.2f} m")
    print(f"  t = {meta['thickness']:.3f} m, elementi = {len(m.elements)}, nodi = {len(m.nodes)}")
    print("  Dominio: sviluppo piano cilindrico, foro alla base, bordo inferiore incastrato")
    print_check("max |w|", max_w, None)
    print_check("equilibrio verticale R+F", total_reaction + total_load, 0.0, tol=0.02)

    save_figure(plot_mesh(m, show_node_ids=False), "cs13_chimney_mesh.png",
                width=950, height=650, title="Mesh ciminiera rastremata")
    save_figure(plot_supports(m), "cs13_chimney_supports.png",
                width=950, height=650, title="Vincoli alla base della ciminiera")
    save_figure(plot_deformed(res, scale=10), "cs13_chimney_deformed.png",
                width=950, height=650, title="Deformata ciminiera (scala 10x)")
    save_figure(plot_contour(res, "w"), "cs13_chimney_w_map.png",
                width=950, height=650, title="Spostamento w [m]")
    save_figure(plot_contour(res, "Mx"), "cs13_chimney_Mx.png",
                width=950, height=650, title="Mx [N m/m]")
    save_figure(plot_contour(res, "My"), "cs13_chimney_My.png",
                width=950, height=650, title="My [N m/m]")
    save_figure(plot_reactions(res), "cs13_chimney_reactions.png",
                width=950, height=650, title="Reazioni vincolari")
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
