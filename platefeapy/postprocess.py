"""Post-processing per piastre: momenti, tagli, spostamenti."""

from __future__ import annotations

import numpy as np


def element_stresses(result, elem_id: int, n: int = 5) -> dict[str, np.ndarray]:
    """Momenti e tagli ai punti di Gauss dell'elemento.

    Restituisce dict con: x, y, Mx, My, Mxy, Qx, Qy.
    """
    model = result.model
    el = model.elements[elem_id]
    ed = el.global_dofs(model.dof_map)
    u_elem = result.U[ed]

    pts_1d = np.linspace(-0.9, 0.9, n)
    Mx_arr, My_arr, Mxy_arr, Qx_arr, Qy_arr = [], [], [], [], []
    x_arr, y_arr = [], []

    coords = el._coords()
    for xi in pts_1d:
        for eta in pts_1d:
            N = el._shape_functions(xi, eta)
            x = float(N @ coords[:, 0])
            y = float(N @ coords[:, 1])
            s = el.stress_at(xi, eta, u_elem)
            x_arr.append(x)
            y_arr.append(y)
            Mx_arr.append(s["Mx"])
            My_arr.append(s["My"])
            Mxy_arr.append(s["Mxy"])
            Qx_arr.append(s["Qx"])
            Qy_arr.append(s["Qy"])

    return {
        "x": np.array(x_arr), "y": np.array(y_arr),
        "Mx": np.array(Mx_arr), "My": np.array(My_arr),
        "Mxy": np.array(Mxy_arr),
        "Qx": np.array(Qx_arr), "Qy": np.array(Qy_arr),
    }


def element_displacements(result, elem_id: int, n: int = 11) -> dict[str, np.ndarray]:
    """Spostamenti w ai punti interni dell'elemento.

    Restituisce dict con: x, y, w.
    """
    model = result.model
    el = model.elements[elem_id]
    ed = el.global_dofs(model.dof_map)
    u_elem = result.U[ed]

    coords = el._coords()
    pts_1d = np.linspace(-1.0, 1.0, n)
    x_arr, y_arr, w_arr = [], [], []

    for xi in pts_1d:
        for eta in pts_1d:
            N = el._shape_functions(xi, eta)
            x = float(N @ coords[:, 0])
            y = float(N @ coords[:, 1])
            w = float(N @ u_elem[0::3])
            x_arr.append(x)
            y_arr.append(y)
            w_arr.append(w)

    return {
        "x": np.array(x_arr), "y": np.array(y_arr), "w": np.array(w_arr),
    }


def deformed_shape(result, scale: float = 1.0, n: int = 11) -> dict:
    """Coordinate deformate di tutti gli elementi.

    Restituisce dict con liste di (x, y, w_scaled) per ogni elemento.
    """
    model = result.model
    data = {}
    for eid in model.elements:
        di = element_displacements(result, eid, n=n)
        data[eid] = {
            "x": di["x"],
            "y": di["y"],
            "w": di["w"] * scale,
        }
    return data


def principal_moments(Mx: float, My: float, Mxy: float) -> tuple[float, float, float]:
    """Momenti principali e angolo di rotazione.

    Restituisce (M1, M2, alpha) dove M1 >= M2 e alpha e' l'angolo
    della direzione principale in radianti.
    """
    avg = (Mx + My) / 2.0
    diff = (Mx - My) / 2.0
    R = np.sqrt(diff**2 + Mxy**2)
    M1 = avg + R
    M2 = avg - R
    alpha = 0.5 * np.arctan2(Mxy, diff)
    return M1, M2, alpha
