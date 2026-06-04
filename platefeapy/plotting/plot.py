"""Visualizzazione con Plotly per piastre."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from platefeapy import postprocess


def _padded_range(values, pad_fraction: float = 0.08) -> list[float]:
    arr = np.asarray(values, dtype=float)
    v_min = float(arr.min())
    v_max = float(arr.max())
    span = v_max - v_min
    if span < 1e-12:
        span = max(abs(v_min), 1.0)
    pad = span * pad_fraction
    return [v_min - pad, v_max + pad]


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
    """Superficie deformata colorata con mesh di riferimento trasparente."""
    model = result.model
    fig = go.Figure()

    for el in model.elements.values():
        coords = el._coords()
        for ii in range(4):
            jj = (ii + 1) % 4
            fig.add_trace(go.Scatter3d(
                x=[coords[ii, 0], coords[jj, 0]],
                y=[coords[ii, 1], coords[jj, 1]],
                z=[0.0, 0.0],
                mode="lines",
                line=dict(color="rgba(70,70,70,0.28)", width=2, dash="dot"),
                name="Riferimento" if ii == 0 and el is next(iter(model.elements.values())) else None,
                showlegend=False,
                hoverinfo="skip",
            ))

    all_x, all_y, all_z = [], [], []
    all_i, all_j, all_k = [], [], []
    all_colors = []
    offset = 0

    for eid in model.elements:
        el = model.elements[eid]
        coords = el._coords()
        ed = el.global_dofs(model.dof_map)
        u_elem = result.U[ed]

        pts_1d = np.linspace(-1.0, 1.0, n)
        elem_x, elem_y, elem_z, elem_w = [], [], [], []
        for xi in pts_1d:
            for eta in pts_1d:
                N = el._shape_functions(xi, eta)
                x = float(N @ coords[:, 0])
                y = float(N @ coords[:, 1])
                w = float(N @ u_elem[0::3])
                elem_x.append(x)
                elem_y.append(y)
                elem_z.append(w * scale)
                elem_w.append(w)

        base = offset
        all_x.extend(elem_x)
        all_y.extend(elem_y)
        all_z.extend(elem_z)
        all_colors.extend(elem_w)

        for ii in range(n - 1):
            for jj in range(n - 1):
                p0 = base + ii * n + jj
                p1 = base + ii * n + jj + 1
                p2 = base + (ii + 1) * n + jj + 1
                p3 = base + (ii + 1) * n + jj
                all_i.extend([p0, p0])
                all_j.extend([p1, p3])
                all_k.extend([p2, p2])

        offset += n * n

    c_arr = np.array(all_colors)
    c_min, c_max = float(c_arr.min()), float(c_arr.max())
    if c_max - c_min < 1e-30:
        c_max = c_min + 1.0

    fig.add_trace(go.Mesh3d(
        x=all_x, y=all_y, z=all_z,
        i=all_i, j=all_j, k=all_k,
        intensity=all_colors,
        colorscale="RdYlBu",
        cmin=c_min,
        cmax=c_max,
        colorbar=dict(title="w [m]"),
        opacity=1.0,
        flatshading=True,
        showlegend=False,
        hovertemplate="x=%{x:.3g}<br>y=%{y:.3g}<br>w=%{customdata:.3e} m<extra></extra>",
        customdata=all_colors,
    ))

    for el in model.elements.values():
        coords = el._coords()
        ed = el.global_dofs(model.dof_map)
        w_nodes = result.U[ed][0::3] * scale
        for ii in range(4):
            jj = (ii + 1) % 4
            fig.add_trace(go.Scatter3d(
                x=[coords[ii, 0], coords[jj, 0]],
                y=[coords[ii, 1], coords[jj, 1]],
                z=[w_nodes[ii], w_nodes[jj]],
                mode="lines", line=dict(color="rgba(0,0,0,0.65)", width=3),
                showlegend=False, hoverinfo="skip",
            ))

    fig.update_layout(
        title=f"Deformata (scala {scale:g})",
        scene=dict(
            xaxis=dict(title="X", range=_padded_range(all_x)),
            yaxis=dict(title="Y", range=_padded_range(all_y)),
            zaxis=dict(title="w", range=_padded_range([0.0, *all_z])),
            aspectmode="data",
            camera=dict(
                projection=dict(type="orthographic"),
                eye=dict(x=1.55, y=-1.75, z=1.05),
            ),
        ),
        margin=dict(l=20, r=20, t=50, b=20),
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
    """Disegna la i-esima forma modale con riferimento trasparente."""
    model = modal_result.model
    phi_i = modal_result.phi[:, i]

    fig = go.Figure()

    for el in model.elements.values():
        coords = el._coords()
        for ii in range(4):
            jj = (ii + 1) % 4
            fig.add_trace(go.Scatter3d(
                x=[coords[ii, 0], coords[jj, 0]],
                y=[coords[ii, 1], coords[jj, 1]],
                z=[0.0, 0.0],
                mode="lines",
                line=dict(color="rgba(70,70,70,0.28)", width=2, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            ))

    all_x, all_y, all_z = [], [], []
    all_i, all_j, all_k = [], [], []
    all_colors = []
    offset = 0

    for eid, el in model.elements.items():
        coords = el._coords()
        ed = el.global_dofs(model.dof_map)
        w_shape = phi_i[ed][0::3]
        w_nodes = w_shape * scale

        pts_1d = np.linspace(-1.0, 1.0, n)
        elem_x, elem_y, elem_z, elem_w = [], [], [], []
        for xi in pts_1d:
            for eta in pts_1d:
                N = el._shape_functions(xi, eta)
                x = float(N @ coords[:, 0])
                y = float(N @ coords[:, 1])
                w = float(N @ w_nodes)
                w_norm = float(N @ w_shape)
                elem_x.append(x)
                elem_y.append(y)
                elem_z.append(w)
                elem_w.append(w_norm)

        base = offset
        all_x.extend(elem_x)
        all_y.extend(elem_y)
        all_z.extend(elem_z)
        all_colors.extend(elem_w)

        for ii in range(n - 1):
            for jj in range(n - 1):
                p0 = base + ii * n + jj
                p1 = base + ii * n + jj + 1
                p2 = base + (ii + 1) * n + jj + 1
                p3 = base + (ii + 1) * n + jj
                all_i.extend([p0, p0])
                all_j.extend([p1, p3])
                all_k.extend([p2, p2])

        offset += n * n

    c_arr = np.array(all_colors)
    c_abs = float(np.max(np.abs(c_arr))) if c_arr.size else 1.0
    if c_abs < 1e-30:
        c_abs = 1.0
    modal_index = (c_arr / c_abs).tolist()

    fig.add_trace(go.Mesh3d(
        x=all_x, y=all_y, z=all_z,
        i=all_i, j=all_j, k=all_k,
        intensity=modal_index,
        colorscale="RdYlBu",
        cmin=-1.0,
        cmax=1.0,
        colorbar=dict(title="w / |w|max"),
        opacity=1.0,
        flatshading=True,
        showlegend=False,
        hovertemplate="x=%{x:.3g}<br>y=%{y:.3g}<br>w/|w|max=%{customdata:.3f}<extra></extra>",
        customdata=modal_index,
    ))

    for el in model.elements.values():
        coords = el._coords()
        ed = el.global_dofs(model.dof_map)
        w_nodes = phi_i[ed][0::3] * scale
        for ii in range(4):
            jj = (ii + 1) % 4
            fig.add_trace(go.Scatter3d(
                x=[coords[ii, 0], coords[jj, 0]],
                y=[coords[ii, 1], coords[jj, 1]],
                z=[w_nodes[ii], w_nodes[jj]],
                mode="lines", line=dict(color="rgba(0,0,0,0.65)", width=3),
                showlegend=False, hoverinfo="skip",
            ))

    f = modal_result.freq[i]
    fig.update_layout(
        title=f"Modo {i + 1} — f = {f:.3f} Hz (T = {1 / f:.3f} s)" if f > 0 else f"Modo {i + 1}",
        scene=dict(
            xaxis=dict(title="X", range=_padded_range(all_x)),
            yaxis=dict(title="Y", range=_padded_range(all_y)),
            zaxis=dict(title="w", range=_padded_range([0.0, *all_z])),
            aspectmode="data",
            camera=dict(
                projection=dict(type="orthographic"),
                eye=dict(x=1.55, y=-1.75, z=1.05),
            ),
        ),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig
