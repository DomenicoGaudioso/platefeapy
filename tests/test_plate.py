"""Test analitici per piastra quadrata semplicemente appoggiata."""

import numpy as np
import pytest

from platefeapy import Model, Material, ShellSection


def _simply_supported_plate(n_elements: int = 4, theory: str = "mindlin"):
    """Piastra quadrata L x L, semplicemente appoggiata, carico uniforme p."""
    L = 1.0
    m = Model()
    n = n_elements + 1
    nid = 1
    for j in range(n):
        for i in range(n):
            m.add_node(nid, i * L / n_elements, j * L / n_elements)
            nid += 1

    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)

    eid = 1
    for j in range(n_elements):
        for i in range(n_elements):
            n1 = j * n + i + 1
            n2 = n1 + 1
            n3 = n2 + n
            n4 = n1 + n
            m.add_plate(eid, [n1, n2, n3, n4], mat, sec, theory=theory)
            eid += 1

    for j in range(n):
        for i in range(n):
            nid = j * n + i + 1
            on_edge_x = (i == 0 or i == n_elements)
            on_edge_y = (j == 0 or j == n_elements)
            if on_edge_x or on_edge_y:
                m.fix(nid, ["w"])

    return m


def test_simply_supported_uniform_pressure():
    """w_max analitico per piastra SS: w = 0.00406 * p * L^4 / D."""
    L = 1.0
    p = -1000.0
    E = 210e9
    nu = 0.3
    t = 0.01
    D = E * t**3 / (12.0 * (1.0 - nu**2))
    w_exact = 0.00406 * abs(p) * L**4 / D

    m = _simply_supported_plate(n_elements=8, theory="mindlin")
    for eid in m.elements:
        m.add_pressure(eid, p)

    res = m.solve()

    w_max = 0.0
    for nid in m.nodes:
        w = abs(res.displacement(nid, "w"))
        w_max = max(w_max, w)

    rel_error = abs(w_max - w_exact) / w_exact
    assert rel_error < 0.15, f"Errore relativo {rel_error:.4f} > 15%"


def test_kirchhoff_plate():
    """Test elemento Kirchhoff ACM."""
    m = _simply_supported_plate(n_elements=4, theory="kirchhoff")
    p = -1000.0
    for eid in m.elements:
        m.add_pressure(eid, p)
    res = m.solve()

    w_max = 0.0
    for nid in m.nodes:
        w = abs(res.displacement(nid, "w"))
        w_max = max(w_max, w)

    assert w_max > 0, "Spostamento massimo nullo"


def test_nodal_load():
    """Test carico nodale concentrato."""
    m = Model()
    m.add_node(1, 0, 0)
    m.add_node(2, 1, 0)
    m.add_node(3, 1, 1)
    m.add_node(4, 0, 1)
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    m.add_plate(1, [1, 2, 3, 4], mat, sec)
    for nid in range(1, 5):
        m.fix(nid, ["w"])
    m.add_nodal_load(1, Fz=-1000.0)
    res = m.solve()
    assert res.U is not None


def test_modal_analysis():
    """Test analisi modale: frequenze positive."""
    m = _simply_supported_plate(n_elements=4)
    for el in m.elements.values():
        el.material.rho = 7850.0
    res = m.modal(n_modes=3)
    assert len(res.freq) == 3
    assert all(f >= 0 for f in res.freq)


def test_settlement():
    """Test cedimento nodale."""
    m = Model()
    m.add_node(1, 0, 0)
    m.add_node(2, 1, 0)
    m.add_node(3, 1, 1)
    m.add_node(4, 0, 1)
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    m.add_plate(1, [1, 2, 3, 4], mat, sec)
    for nid in range(1, 5):
        m.fix(nid, ["w"])
    m.add_settlement(1, "w", -0.001)
    res = m.solve()
    w1 = res.displacement(1, "w")
    assert abs(w1 - (-0.001)) < 1e-10


def test_stiffness_symmetry():
    """La matrice di rigidezza deve essere simmetrica."""
    m = Model()
    m.add_node(1, 0, 0)
    m.add_node(2, 1, 0)
    m.add_node(3, 1, 1)
    m.add_node(4, 0, 1)
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    m.add_plate(1, [1, 2, 3, 4], mat, sec)
    K = m.assemble_stiffness()
    assert np.allclose(K, K.T, atol=1e-10)


def test_stiffness_positive_diagonal():
    """La diagonale di K deve essere non negativa."""
    m = Model()
    m.add_node(1, 0, 0)
    m.add_node(2, 1, 0)
    m.add_node(3, 1, 1)
    m.add_node(4, 0, 1)
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    m.add_plate(1, [1, 2, 3, 4], mat, sec)
    K = m.assemble_stiffness()
    assert np.all(np.diag(K) >= -1e-15)
