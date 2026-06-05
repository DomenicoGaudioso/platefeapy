"""Caso studio CS13: ciminiera shell 3D rastremata con apertura."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import plotly.graph_objects as go

from platefeapy import Material, ShellModel, ShellSection

try:
    from .common import header, print_check, save_figure
except ImportError:  # pragma: no cover - standalone execution
    from common import header, print_check, save_figure


def radius_at_height(z: float, H: float, r_base: float, r_top: float) -> float:
    return r_base + (r_top - r_base) * z / H


def wind_pressure(theta: float, z: float, H: float) -> float:
    q_top = 500.0
    q_z = q_top * (0.35 + 0.65 * (z / H) ** 0.25)
    cp = max(0.0, np.cos(theta)) + 0.18 * max(0.0, -np.cos(theta))
    return -q_z * cp


def _inside_service_opening(theta: float, z: float, H: float,
                            r_base: float, r_top: float) -> bool:
    r = radius_at_height(z, H, r_base, r_top)
    return abs(theta * r) < 1.45 and 3.0 < z < 12.0


def _xyz(theta: float, z: float, H: float, r_base: float, r_top: float) -> tuple[float, float, float]:
    r = radius_at_height(z, H, r_base, r_top)
    return r * np.cos(theta), r * np.sin(theta), z


def build_chimney_shell(ntheta: int = 24, nz: int = 32):
    """Costruisce una ciminiera shell sulla geometria cilindrica reale."""
    H = 60.0
    r_base = 3.0
    r_top = 2.05
    thickness = 0.40
    mat = Material(E=30e9, nu=0.20)
    sec = ShellSection(t=thickness)

    theta_vals = np.linspace(-np.pi, np.pi, ntheta, endpoint=False)
    z_vals = np.linspace(0.0, H, nz + 1)

    kept_cells: list[tuple[int, int]] = []
    used: set[tuple[int, int]] = set()
    for j in range(nz):
        z_c = 0.5 * (z_vals[j] + z_vals[j + 1])
        for i, theta0 in enumerate(theta_vals):
            theta1 = theta_vals[(i + 1) % ntheta] + (2.0 * np.pi if i == ntheta - 1 else 0.0)
            theta_c = ((0.5 * (theta0 + theta1) + np.pi) % (2.0 * np.pi)) - np.pi
            if _inside_service_opening(theta_c, z_c, H, r_base, r_top):
                continue
            kept_cells.append((i, j))
            used.update({(i, j), ((i + 1) % ntheta, j), ((i + 1) % ntheta, j + 1), (i, j + 1)})

    m = ShellModel()
    node_map: dict[tuple[int, int], int] = {}
    node_theta: dict[int, float] = {}
    node_z: dict[int, float] = {}
    nid = 1
    for i, j in sorted(used, key=lambda p: (p[1], p[0])):
        theta = theta_vals[i]
        z = z_vals[j]
        x, y, zz = _xyz(theta, z, H, r_base, r_top)
        m.add_node(nid, x, y, zz)
        node_map[(i, j)] = nid
        node_theta[nid] = theta
        node_z[nid] = z
        nid += 1

    elem_theta_z: dict[int, tuple[float, float]] = {}
    eid = 1
    for i, j in kept_cells:
        ip = (i + 1) % ntheta
        nodes = [
            node_map[(i, j)],
            node_map[(ip, j)],
            node_map[(ip, j + 1)],
            node_map[(i, j + 1)],
        ]
        m.add_shell(eid, nodes, mat, sec)
        theta0 = theta_vals[i]
        theta1 = theta_vals[ip] + (2.0 * np.pi if i == ntheta - 1 else 0.0)
        theta_c = ((0.5 * (theta0 + theta1) + np.pi) % (2.0 * np.pi)) - np.pi
        z_c = 0.5 * (z_vals[j] + z_vals[j + 1])
        elem_theta_z[eid] = (theta_c, z_c)
        eid += 1

    base_nodes = [nid for nid, z in node_z.items() if abs(z) < 1e-12]
    for nid in base_nodes:
        m.fix(nid)

    return m, elem_theta_z, {
        "H": H,
        "r_base": r_base,
        "r_top": r_top,
        "thickness": thickness,
        "node_theta": node_theta,
        "node_z": node_z,
        "base_nodes": base_nodes,
    }


def radial_displacement(res, meta: dict, nid: int) -> float:
    theta = meta["node_theta"][nid]
    er = np.array([np.cos(theta), np.sin(theta), 0.0])
    return float(res.displacements(nid)[:3] @ er)


def _mesh_arrays(m: ShellModel, values: dict[int, float] | None = None,
                 scale: float = 0.0, meta: dict | None = None):
    x: list[float] = []
    y: list[float] = []
    z: list[float] = []
    i: list[int] = []
    j: list[int] = []
    k: list[int] = []
    c: list[float] = []
    offset = 0
    for el in m.elements.values():
        pts = []
        for nid in el.node_ids:
            p = m.nodes[nid].coords.copy()
            val = 0.0 if values is None else values[nid]
            if meta is not None and scale:
                theta = meta["node_theta"][nid]
                p += scale * val * np.array([np.cos(theta), np.sin(theta), 0.0])
            pts.append(p)
            c.append(val)
        x.extend([float(p[0]) for p in pts])
        y.extend([float(p[1]) for p in pts])
        z.extend([float(p[2]) for p in pts])
        i.extend([offset, offset])
        j.extend([offset + 1, offset + 2])
        k.extend([offset + 2, offset + 3])
        offset += 4
    return x, y, z, i, j, k, c


def _chimney_scene() -> dict:
    return dict(
        xaxis=dict(title="X", range=[-4.2, 4.2]),
        yaxis=dict(title="Y", range=[-4.2, 4.2]),
        zaxis=dict(title="Z", range=[0.0, 60.0]),
        aspectmode="manual",
        aspectratio=dict(x=1.0, y=1.0, z=1.45),
        camera=dict(
            projection=dict(type="orthographic"),
            eye=dict(x=1.8, y=-2.4, z=0.35),
        ),
    )


def plot_shell_mesh(m: ShellModel) -> go.Figure:
    fig = go.Figure()
    for el in m.elements.values():
        pts = [m.nodes[nid].coords for nid in el.node_ids]
        for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
            fig.add_trace(go.Scatter3d(
                x=[pts[a][0], pts[b][0]], y=[pts[a][1], pts[b][1]], z=[pts[a][2], pts[b][2]],
                mode="lines", line=dict(color="#444", width=2), showlegend=False,
                hoverinfo="skip",
            ))
    fig.update_layout(
        title="Mesh shell 3D ciminiera",
        scene=_chimney_scene(),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def plot_shell_deformed(res, meta: dict, scale: float) -> go.Figure:
    vals = {nid: radial_displacement(res, meta, nid) for nid in res.model.nodes}
    x, y, z, i, j, k, c = _mesh_arrays(res.model, vals, scale=scale, meta=meta)
    fig = go.Figure(go.Mesh3d(
        x=x, y=y, z=z, i=i, j=j, k=k, intensity=c, colorscale="RdYlBu",
        colorbar=dict(title="u_rad [m]"), flatshading=True,
    ))
    fig.update_layout(
        title=f"Deformata shell 3D ciminiera (scala {scale:g}x)",
        scene=_chimney_scene(),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def plot_shell_supports(m: ShellModel, meta: dict) -> go.Figure:
    fig = plot_shell_mesh(m)
    pts = [m.nodes[nid].coords for nid in meta["base_nodes"]]
    fig.add_trace(go.Scatter3d(
        x=[p[0] for p in pts], y=[p[1] for p in pts], z=[p[2] for p in pts],
        mode="markers", marker=dict(size=5, color="#111", symbol="diamond"),
        name="Vincoli", showlegend=True,
    ))
    fig.update_layout(title="Vincoli shell 3D ciminiera")
    return fig


def plot_shell_reactions(res, meta: dict) -> go.Figure:
    fig = plot_shell_supports(res.model, meta)
    vals = [np.linalg.norm(res.reactions(nid)[:3]) for nid in meta["base_nodes"]]
    max_r = max(vals) if vals else 1.0
    L = 0.7
    for nid in meta["base_nodes"]:
        rvec = res.reactions(nid)[:3]
        mag = np.linalg.norm(rvec)
        if mag < 1e-9 * max_r:
            continue
        p0 = res.model.nodes[nid].coords
        p1 = p0 + rvec / mag * L * mag / max_r
        fig.add_trace(go.Scatter3d(
            x=[p0[0], p1[0]], y=[p0[1], p1[1]], z=[p0[2], p1[2]],
            mode="lines", line=dict(color="#15803d", width=5), showlegend=False,
            hovertemplate=f"R={mag:.3e} N<extra></extra>",
        ))
    fig.update_layout(title="Reazioni shell 3D ciminiera")
    return fig


def main() -> None:
    m, elem_theta_z, meta = build_chimney_shell()
    H = meta["H"]
    for eid, (theta, z) in elem_theta_z.items():
        m.add_pressure(eid, wind_pressure(theta, z, H))

    res = m.solve()
    radial_vals = [abs(radial_displacement(res, meta, nid)) for nid in m.nodes]
    max_ur = max(radial_vals)

    header("CS13 - Ciminiera shell 3D rastremata con apertura")
    print(f"  H = {H:.1f} m, r_base = {meta['r_base']:.2f} m, r_top = {meta['r_top']:.2f} m")
    print(f"  t = {meta['thickness']:.3f} m, elementi = {len(m.elements)}, nodi = {len(m.nodes)}")
    print("  Geometria: cilindrica 3D reale, apertura di servizio, base incastrata")
    print_check("max |u_radiale|", max_ur, 3.306855e-03, tol=0.10)

    save_figure(plot_shell_mesh(m), "cs13_chimney_mesh.png",
                width=950, height=900, title="Mesh shell 3D ciminiera")
    save_figure(plot_shell_supports(m, meta), "cs13_chimney_supports.png",
                width=950, height=900, title="Vincoli shell 3D")
    save_figure(plot_shell_deformed(res, meta, scale=120), "cs13_chimney_deformed.png",
                width=950, height=900, title="Deformata shell 3D (scala 120x)")
    save_figure(plot_shell_deformed(res, meta, scale=0), "cs13_chimney_w_map.png",
                width=950, height=900, title="Spostamento radiale reale [m]")
    save_figure(plot_shell_reactions(res, meta), "cs13_chimney_reactions.png",
                width=950, height=900, title="Reazioni shell 3D")
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
