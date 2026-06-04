"""Visualizzazione con Plotly per piastre."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from platefeapy import postprocess


def plot_mesh(model, show_node_ids: bool = True) -> go.Figure:
    """Disegna la mesh della piastra."""
    fig = go.Figure()
    for el in model.elements.values():
        coords = el._coords()
        x = list(coords[:, 0]) + [coords[0, 0]]
        y = list(coords[:, 1]) + [coords[0, 1]]
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines",
            line=dict(color="#444", width=2),
            showlegend=False,
        ))
    xs = [n.x for n in model.nodes.values()]
    ys = [n.y for n in model.nodes.values()]
    text = [str(n.id) for n in model.nodes.values()] if show_node_ids else None
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text" if show_node_ids else "markers",
        marker=dict(size=6, color="#1f77b4"), text=text, textposition="top center",
        showlegend=False,
    ))
    fig.update_layout(
        title="Mesh",
        xaxis_title="X", yaxis_title="Y",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def plot_deformed(result, scale: float = 1.0, n: int = 21) -> go.Figure:
    """Superficie deformata della piastra."""
    model = result.model
    fig = go.Figure()

    all_x, all_y, all_z = [], [], []
    for eid in model.elements:
        di = postprocess.element_displacements(result, eid, n=n)
        all_x.extend(di["x"])
        all_y.extend(di["y"])
        all_z.extend(di["w"] * scale)

    fig.add_trace(go.Scatter3d(
        x=all_x, y=all_y, z=all_z,
        mode="markers", marker=dict(size=2, color=all_z, colorscale="RdYlBu"),
        showlegend=False,
    ))

    for el in model.elements.values():
        coords = el._coords()
        ed = el.global_dofs(model.dof_map)
        w_nodes = result.U[ed][0::3] * scale
        for i in range(4):
            j = (i + 1) % 4
            fig.add_trace(go.Scatter3d(
                x=[coords[i, 0], coords[j, 0]],
                y=[coords[i, 1], coords[j, 1]],
                z=[w_nodes[i], w_nodes[j]],
                mode="lines", line=dict(color="#444", width=3),
                showlegend=False,
            ))

    fig.update_layout(
        title=f"Deformata (scala {scale:g})",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="w",
                   aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


def plot_contour(result, component: str = "Mx", n: int = 11,
                 title: str | None = None) -> go.Figure:
    """Mappa a colori di una componente (Mx, My, Mxy, Qx, Qy, w)."""
    model = result.model
    fig = go.Figure()

    all_x, all_y, all_v = [], [], []
    for eid in model.elements:
        if component == "w":
            di = postprocess.element_displacements(result, eid, n=n)
            all_v.extend(di["w"])
        else:
            di = postprocess.element_stresses(result, eid, n=n)
            all_v.extend(di[component])
        all_x.extend(di["x"])
        all_y.extend(di["y"])

    fig.add_trace(go.Scatter(
        x=all_x, y=all_y, mode="markers",
        marker=dict(size=8, color=all_v, colorscale="RdYlBu",
                    colorbar=dict(title=component)),
        showlegend=False,
    ))

    for el in model.elements.values():
        coords = el._coords()
        x = list(coords[:, 0]) + [coords[0, 0]]
        y = list(coords[:, 1]) + [coords[0, 1]]
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines",
            line=dict(color="#444", width=1),
            showlegend=False,
        ))

    fig.update_layout(
        title=title or f"Mappa {component}",
        xaxis_title="X", yaxis_title="Y",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def plot_reactions(result, scale: float = 1.0) -> go.Figure:
    """Reazioni vincolari ai nodi."""
    model = result.model
    fig = go.Figure()

    for el in model.elements.values():
        coords = el._coords()
        x = list(coords[:, 0]) + [coords[0, 0]]
        y = list(coords[:, 1]) + [coords[0, 1]]
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines",
            line=dict(color="#ccc", width=1),
            showlegend=False,
        ))

    Fmax = 1e-30
    for nid in model.nodes:
        R = result.reactions(nid)
        Fmax = max(Fmax, abs(R[0]))

    for nid in model.nodes:
        R = result.reactions(nid)
        c = model.nodes[nid]
        if abs(R[0]) > 1e-6 * Fmax:
            fig.add_trace(go.Scatter(
                x=[c.x], y=[c.y], mode="markers+text",
                marker=dict(size=12, color="#2ca02c", symbol="triangle-up"),
                text=[f"Fz={R[0]:.3g}"],
                textposition="top center",
                showlegend=False,
            ))

    fig.update_layout(
        title="Reazioni vincolari",
        xaxis_title="X", yaxis_title="Y",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def plot_mode(modal_result, i: int = 0, scale: float = 1.0,
              n: int = 21) -> go.Figure:
    """Disegna la i-esima forma modale."""
    model = modal_result.model
    phi_i = modal_result.phi[:, i]

    fig = go.Figure()
    all_x, all_y, all_z = [], [], []
    for eid, el in model.elements.items():
        coords = el._coords()
        ed = el.global_dofs(model.dof_map)
        w_nodes = phi_i[ed][0::3] * scale
        pts_1d = np.linspace(-1.0, 1.0, n)
        for xi in pts_1d:
            for eta in pts_1d:
                N = el._shape_functions(xi, eta)
                x = float(N @ coords[:, 0])
                y = float(N @ coords[:, 1])
                w = float(N @ w_nodes)
                all_x.append(x)
                all_y.append(y)
                all_z.append(w)

    fig.add_trace(go.Scatter3d(
        x=all_x, y=all_y, z=all_z,
        mode="markers", marker=dict(size=2, color=all_z, colorscale="RdYlBu"),
        showlegend=False,
    ))

    f = modal_result.freq[i]
    fig.update_layout(
        title=f"Modo {i + 1} — f = {f:.3f} Hz (T = {1 / f:.3f} s)" if f > 0 else f"Modo {i + 1}",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="w",
                   aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig
