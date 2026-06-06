"""Caso studio CS14: cassone sottile shell 3D a mensola."""
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


def _add_node_unique(m: ShellModel, node_map: dict[tuple[float, float, float], int],
                     xyz: tuple[float, float, float]) -> int:
    key = tuple(round(v, 10) for v in xyz)
    if key not in node_map:
        nid = len(node_map) + 1
        m.add_node(nid, *key)
        node_map[key] = nid
    return node_map[key]


def _surface_grid(m: ShellModel, node_map: dict, xs, ys, zs, fixed_axis: str):
    ids = {}
    for i, x in enumerate(xs):
        for j, a in enumerate(ys if fixed_axis != "y" else zs):
            if fixed_axis == "z":
                xyz = (x, a, zs)
            elif fixed_axis == "y":
                xyz = (x, ys, a)
            else:
                xyz = (xs, x, a)
            ids[(i, j)] = _add_node_unique(m, node_map, xyz)
    return ids


def build_box_girder_shell(nx: int = 18, n_per_wall: int = 3):
    """Costruisce un cassone rettangolare sottile con superfici shell 3D."""
    L = 6.0
    b = 1.20
    h = 0.90
    t = 0.06
    E = 210e9
    nu = 0.30
    P = -25_000.0
    mat = Material(E=E, nu=nu)
    sec = ShellSection(t=t)

    m = ShellModel()
    node_map: dict[tuple[float, float, float], int] = {}
    xs = np.linspace(0.0, L, nx + 1)
    ys = np.linspace(-b / 2, b / 2, n_per_wall + 1)
    zs = np.linspace(-h / 2, h / 2, n_per_wall + 1)
    eid = 1

    # Top e bottom.
    for z in (-h / 2, h / 2):
        ids = _surface_grid(m, node_map, xs, ys, z, "z")
        for i in range(nx):
            for j in range(n_per_wall):
                nodes = [ids[(i, j)], ids[(i + 1, j)], ids[(i + 1, j + 1)], ids[(i, j + 1)]]
                m.add_shell(eid, nodes, mat, sec)
                eid += 1

    # Anime laterali.
    for y in (-b / 2, b / 2):
        ids = _surface_grid(m, node_map, xs, y, zs, "y")
        for i in range(nx):
            for j in range(n_per_wall):
                nodes = [ids[(i, j)], ids[(i + 1, j)], ids[(i + 1, j + 1)], ids[(i, j + 1)]]
                m.add_shell(eid, nodes, mat, sec)
                eid += 1

    fixed_nodes = [nid for nid, node in m.nodes.items() if abs(node.x) < 1e-12]
    tip_nodes = [nid for nid, node in m.nodes.items() if abs(node.x - L) < 1e-12]
    for nid in fixed_nodes:
        m.fix(nid)
    for nid in tip_nodes:
        m.add_nodal_load(nid, uz=P / len(tip_nodes))

    meta = {
        "L": L, "b": b, "h": h, "t": t, "E": E, "nu": nu, "P": P,
        "fixed_nodes": fixed_nodes, "tip_nodes": tip_nodes,
    }
    return m, meta


def _mesh_arrays(m: ShellModel, result=None, scale: float = 0.0):
    values = {}
    if result is not None:
        values = {nid: float(np.linalg.norm(result.displacements(nid)[:3])) for nid in m.nodes}
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
            if result is not None:
                p += scale * result.displacements(nid)[:3]
            pts.append(p)
            c.append(values.get(nid, 0.0))
        x.extend([float(p[0]) for p in pts])
        y.extend([float(p[1]) for p in pts])
        z.extend([float(p[2]) for p in pts])
        i.extend([offset, offset])
        j.extend([offset + 1, offset + 2])
        k.extend([offset + 2, offset + 3])
        offset += 4
    return x, y, z, i, j, k, c


def _reference_wire(m: ShellModel):
    traces = []
    for el in m.elements.values():
        pts = [m.nodes[nid].coords for nid in el.node_ids]
        for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
            traces.append(go.Scatter3d(
                x=[pts[a][0], pts[b][0]], y=[pts[a][1], pts[b][1]], z=[pts[a][2], pts[b][2]],
                mode="lines", line=dict(color="rgba(30,30,30,0.22)", width=2),
                hoverinfo="skip", showlegend=False,
            ))
    return traces


def _scene():
    return dict(
        xaxis=dict(title="X", range=[-0.2, 6.4]),
        yaxis=dict(title="Y", range=[-0.95, 0.95]),
        zaxis=dict(title="Z", range=[-0.75, 0.75]),
        aspectmode="manual",
        aspectratio=dict(x=3.4, y=1.0, z=1.0),
        camera=dict(projection=dict(type="orthographic"), eye=dict(x=1.7, y=-2.0, z=0.9)),
    )


def plot_shell_mesh(m: ShellModel) -> go.Figure:
    fig = go.Figure(_reference_wire(m))
    fig.update_layout(scene=_scene(), margin=dict(l=10, r=10, t=50, b=10))
    return fig


def plot_shell_deformed(res, scale: float) -> go.Figure:
    x, y, z, i, j, k, c = _mesh_arrays(res.model, res, scale)
    fig = go.Figure(_reference_wire(res.model))
    fig.add_trace(go.Mesh3d(
        x=x, y=y, z=z, i=i, j=j, k=k, intensity=c, colorscale="Turbo",
        colorbar=dict(title="|u| [m]"), opacity=1.0, flatshading=True,
        name="Deformata",
    ))
    fig.update_layout(scene=_scene(), margin=dict(l=10, r=10, t=50, b=10))
    return fig


def plot_shell_supports(m: ShellModel, meta: dict) -> go.Figure:
    fig = plot_shell_mesh(m)
    pts = [m.nodes[nid].coords for nid in meta["fixed_nodes"]]
    fig.add_trace(go.Scatter3d(
        x=[p[0] for p in pts], y=[p[1] for p in pts], z=[p[2] for p in pts],
        mode="markers", marker=dict(size=4, color="#111", symbol="diamond"),
        name="Vincoli",
    ))
    return fig


def plot_shell_reactions(res, meta: dict) -> go.Figure:
    fig = plot_shell_supports(res.model, meta)
    vals = [np.linalg.norm(res.reactions(nid)[:3]) for nid in meta["fixed_nodes"]]
    max_r = max(vals) if vals else 1.0
    for nid in meta["fixed_nodes"]:
        r = res.reactions(nid)[:3]
        mag = np.linalg.norm(r)
        if mag < 1e-9 * max_r:
            continue
        p0 = res.model.nodes[nid].coords
        p1 = p0 + 0.45 * r / mag * mag / max_r
        fig.add_trace(go.Scatter3d(
            x=[p0[0], p1[0]], y=[p0[1], p1[1]], z=[p0[2], p1[2]],
            mode="lines", line=dict(color="#15803d", width=5),
            hovertemplate=f"R={mag:.3e} N<extra></extra>", showlegend=False,
        ))
    return fig


def main() -> None:
    m, meta = build_box_girder_shell()
    res = m.solve()
    tip_w = float(np.mean([res.displacement(nid, "uz") for nid in meta["tip_nodes"]]))
    max_u = max(float(np.linalg.norm(res.displacements(nid)[:3])) for nid in m.nodes)

    header("CS14 - Cassone sottile shell 3D a mensola")
    print(f"  L = {meta['L']:.2f} m, b = {meta['b']:.2f} m, h = {meta['h']:.2f} m, t = {meta['t']:.3f} m")
    print(f"  Elementi shell = {len(m.elements)}, nodi = {len(m.nodes)}")
    print(f"  Carico verticale in estremita' P = {meta['P']:.1f} N")
    print_check("w medio in punta", tip_w, -2.936810e-04, tol=0.20)
    print_check("max |u|", max_u, None)

    save_figure(plot_shell_mesh(m), "cs14_box_shell_mesh.png",
                width=1100, height=720, title="Cassone shell 3D - mesh")
    save_figure(plot_shell_supports(m, meta), "cs14_box_shell_supports.png",
                width=1100, height=720, title="Cassone shell 3D - vincoli")
    save_figure(plot_shell_deformed(res, scale=180), "cs14_box_shell_deformed.png",
                width=1100, height=720, title="Cassone shell 3D - deformata (scala 180x)")
    save_figure(plot_shell_reactions(res, meta), "cs14_box_shell_reactions.png",
                width=1100, height=720, title="Cassone shell 3D - reazioni")
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
