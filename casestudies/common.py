"""Helper condivisi per i casi studio platefeapy.

Fornisce:
- save_figure(fig, name): esporta un plotly figure in PNG (kaleido) nella cartella images/
- rect_plate_mesh(Lx, Ly, n_ex, n_ey, theory): costruisce una piastra rettangolare meshata
- build_ss_bc(m, axis): vincoli SS (w=0) sui bordi
- build_clamped_bc(m): vincoli incastrati sui bordi
- navier_w_max(p, L, E, nu, t): formula Navier per piastra SS
- timoshenko_clamped_w_max(p, L, E, nu, t): formula Timoshenko per piastra incastrata
- print_check(label, fem, exact, tol): stampa confronto con tolleranza
"""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np

CASESTUDIES_DIR = Path(__file__).resolve().parent
IMAGES_DIR = CASESTUDIES_DIR / "images"
DOC_IMAGES_DIR = CASESTUDIES_DIR.parent / "docs" / "casestudies" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DOC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def save_figure(fig, name: str, width: int = 800, height: int = 600,
                scale: int = 1, title: str | None = None) -> Path:
    """Salva una figura Plotly come PNG in casestudies/images/."""
    if title is not None:
        fig.update_layout(title=title)
    fig.update_layout(width=width, height=height)
    out = IMAGES_DIR / name
    fig.write_image(str(out), scale=scale)
    shutil.copy2(out, DOC_IMAGES_DIR / name)
    return out


def rect_plate_mesh(m, Lx: float, Ly: float, n_ex: int, n_ey: int,
                    mat, sec, theory: str = "mindlin") -> None:
    """Costruisce la mesh di una piastra rettangolare Lx x Ly (orientata X-Y)."""
    nx = n_ex + 1
    ny = n_ey + 1
    nid = 1
    for j in range(ny):
        for i in range(nx):
            m.add_node(nid, i * Lx / n_ex, j * Ly / n_ey)
            nid += 1
    eid = 1
    for j in range(n_ey):
        for i in range(n_ex):
            n1 = j * nx + i + 1
            n2 = n1 + 1
            n3 = n2 + nx
            n4 = n1 + nx
            m.add_plate(eid, [n1, n2, n3, n4], mat, sec, theory=theory)
            eid += 1


def build_ss_bc(m, axis: str = "all") -> None:
    """Vincoli di appoggio semplice (w=0) sui bordi della mesh rettangolare.

    axis:
        'all'   -> tutti e quattro i lati
        'x'     -> solo lati x=0 e x=Lx
        'y'     -> solo lati y=0 e y=Ly
    """
    nodes_xy = sorted([(n.x, n.y, n.id) for n in m.nodes.values()])
    xs = sorted({x for x, _, _ in nodes_xy})
    ys = sorted({y for _, y, _ in nodes_xy})
    x_lo, x_hi = xs[0], xs[-1]
    y_lo, y_hi = ys[0], ys[-1]
    for x, y, nid in nodes_xy:
        on_x_edge = (x == x_lo) or (x == x_hi)
        on_y_edge = (y == y_lo) or (y == y_hi)
        if axis == "all" and (on_x_edge or on_y_edge):
            m.fix(nid, ["w"])
        elif axis == "x" and on_x_edge:
            m.fix(nid, ["w"])
        elif axis == "y" and on_y_edge:
            m.fix(nid, ["w"])


def build_clamped_bc(m) -> None:
    """Vincoli di incastro (w, theta_x, theta_y = 0) sui bordi della mesh."""
    nodes_xy = sorted([(n.x, n.y, n.id) for n in m.nodes.values()])
    xs = sorted({x for x, _, _ in nodes_xy})
    ys = sorted({y for _, y, _ in nodes_xy})
    x_lo, x_hi = xs[0], xs[-1]
    y_lo, y_hi = ys[0], ys[-1]
    for x, y, nid in nodes_xy:
        if x in (x_lo, x_hi) or y in (y_lo, y_hi):
            m.fix(nid)


def build_free_bc(m) -> None:
    """Nessun vincolo perimetrale: serve per piastra Levy con due lati liberi."""
    return


def D_bending(E: float, nu: float, t: float) -> float:
    return E * t ** 3 / (12.0 * (1.0 - nu ** 2))


def navier_ss_wmax(p: float, L: float, E: float, nu: float, t: float) -> float:
    """w_max al centro per piastra quadrata SS con pressione uniforme (Navier).

    w_max = alpha * p * L^4 / D
    con alpha = 0.00406 (per quadrata, Poisson=0.3).
    """
    D = D_bending(E, nu, t)
    return 0.00406 * abs(p) * L ** 4 / D


def timoshenko_clamped_wmax(p: float, L: float, E: float, nu: float, t: float) -> float:
    """w_max al centro per piastra quadrata incastrata con UDL (Timoshenko).

    w_max = 0.00126 * p * L^4 / D
    """
    D = D_bending(E, nu, t)
    return 0.00126 * abs(p) * L ** 4 / D


def levy_wmax(a: float, b: float, p: float, E: float, nu: float, t: float) -> float:
    """w_max per piastra Levy (lati y=0 e y=b appoggiati, lati x=0 e x=a liberi).

    Coefficiente alpha(a/b, nu) interpolato da Timoshenko & Woinowsky-Krieger
    "Theory of Plates and Shells", 2nd ed., Tab. 3, p. 197, colonna
    "Two opposite edges simply supported, the other two edges free" con nu=0.30.
    Il lato libero e' a (lungo x), il lato appoggiato e' b (lungo y).

    NB: il coefficiente cresce fino a ~0.0138 per piastre molto allungate
    (a/b >> 1), dove il comportamento tende a quello di una trave caricata
    uniformemente su due appoggi con sbalzi.
    """
    ratio = a / b
    table = {
        0.5: 0.00728, 0.667: 0.00910, 1.0: 0.01078, 1.5: 0.01265,
        2.0: 0.01336, 2.5: 0.01366, 3.0: 0.01380,
    }
    rs = sorted(table.keys())
    if ratio <= rs[0]:
        alpha = table[rs[0]]
    elif ratio >= rs[-1]:
        alpha = table[rs[-1]]
    else:
        for k in range(len(rs) - 1):
            if rs[k] <= ratio <= rs[k + 1]:
                x0, x1 = rs[k], rs[k + 1]
                y0, y1 = table[x0], table[x1]
                alpha = y0 + (y1 - y0) * (ratio - x0) / (x1 - x0)
                break
    D = D_bending(E, nu, t)
    return alpha * abs(p) * a ** 4 / D


def trefethen_lambda_ss(nu: float) -> float:
    """Coefficiente di Trefethen per piastra SS sotto carico concentrato centrale.

    Per piastra quadrata SS, carico concentrato P al centro, nu=0.3:
        w_max = lambda * P * L^2 / (pi^4 * D)
    con lambda = 1.0 circa (Trefethen 1959). Per confronto con la formula
    Timoshenko classica w_max = 0.01160 * P * L^2 / D, lambda * L^2 / pi^4
    e' circa 0.0119, molto prossimo.
    """
    return 1.0


def w_point_load_ss_square(P: float, L: float, E: float, nu: float, t: float) -> float:
    """w_max al centro per piastra quadrata SS sotto carico concentrato P.

    Coefficiente 0.01160 (Timoshenko, Theory of Plates and Shells, 2nd ed.,
    Tab. 4, p. 124, caso "central concentrated load P on a square SS plate",
    nu = 0.3).
    """
    D = D_bending(E, nu, t)
    return 0.01160 * abs(P) * L ** 2 / D


def timoshenko_circular_ss_wmax(p: float, R: float, E: float, nu: float, t: float) -> float:
    """w_max al centro per piastra circolare SS, pressione uniforme.

    w_max = (3 + nu) * p * R^4 / (64 * (1 - nu) * D)
    """
    D = D_bending(E, nu, t)
    return (3.0 + nu) * abs(p) * R ** 4 / (64.0 * (1.0 - nu) * D)


def timoshenko_circular_clamped_wmax(p: float, R: float, E: float, nu: float, t: float) -> float:
    """w_max al centro per piastra circolare incastrata, pressione uniforme.

    w_max = p * R^4 / (64 * D)
    """
    D = D_bending(E, nu, t)
    return abs(p) * R ** 4 / (64.0 * D)


def navier_modal_freq(m: int, n: int, L: float, E: float, nu: float,
                      t: float, rho: float) -> float:
    """Frequenza naturale modi (m,n) per piastra SS (Navier)."""
    D = D_bending(E, nu, t)
    mass_per_area = rho * t
    return (np.pi / (2.0 * L ** 2)) * np.sqrt(D / mass_per_area) * (m ** 2 + n ** 2)


def point_load_infinite_plate_wmax(P: float, E: float, nu: float, t: float) -> float:
    """w_max sotto carico concentrato su lastra infinita Kirchhoff.

    w_max = P * L^2 / (8 * pi * D)  con L=1 per piastra SS confronto
    Equivalente: w(r=0) = P/(8*D) * (1+nu)/(1-nu) * 1/(4*pi) ? Usiamo Timoshenko p.122:
    Per piastra infinita, w(0) = P/(8 pi D) * (1+nu)*log(...) - dipende dal dominio.
    Per una piastra SS di lato L caricata in centro, Timoshenko fornisce il
    coefficiente 0.01160 (per quadrata SS, carico centrale)."""
    return None


def print_check(label: str, fem, exact, tol: float = 0.10) -> None:
    """Stampa un confronto fem vs esatto."""
    if exact is None or exact == 0:
        print(f"  {label:<30s} FEM = {fem:.6e}")
        return
    err = abs(fem - exact) / abs(exact) * 100.0
    flag = "OK " if err < tol * 100 else "WARN"
    print(f"  [{flag}] {label:<30s} FEM = {fem:.6e}  esatto = {exact:.6e}  err = {err:6.2f}%")


def header(title: str, char: str = "=") -> None:
    line = char * 72
    print(line)
    print(f"  {title}")
    print(line)
