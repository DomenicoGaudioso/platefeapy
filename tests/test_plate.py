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


def test_plot_contour_adds_isolines():
    m = _simply_supported_plate(n_elements=2)
    for eid in m.elements:
        m.add_pressure(eid, -1000.0)
    res = m.solve()

    from platefeapy.plotting import plot_contour
    fig = plot_contour(res, "w", n=5, n_isolines=4)

    assert any(trace.type == "scatter" and trace.mode == "lines" for trace in fig.data)


def test_plot_supports_adds_constrained_nodes():
    m = _simply_supported_plate(n_elements=2)

    from platefeapy.plotting import plot_supports
    fig = plot_supports(m)

    assert any(trace.name == "Vincoli" for trace in fig.data)


def test_circular_case_mesh_stays_inside_disk():
    from casestudies.cs04_circular import build_circular_plate

    R = 1.0
    m, elems, node_ids, boundary_ids = build_circular_plate(R, 12, bc="ss")
    used_nodes = {nid for elem in m.elements.values() for nid in elem.node_ids}

    assert len(elems) > 12 * 12
    assert len(node_ids) == len(m.nodes)
    assert used_nodes == set(m.nodes)
    assert all(np.hypot(node.x, node.y) <= R + 1e-12 for node in m.nodes.values())
    assert boundary_ids


def test_chimney_case_has_opening_and_base_supports():
    from casestudies.cs13_chimney import build_chimney_shell

    m, elem_theta_z, meta = build_chimney_shell(ntheta=8, nz=12)
    centers = []
    for eid, el in m.elements.items():
        coords = el._coords3d()
        centers.append(coords.mean(axis=0))

    assert elem_theta_z
    assert len(m.elements) < 8 * 12
    assert any(abs(c[0]) > 0.5 for c in centers)
    assert any(abs(c[1]) > 0.5 for c in centers)
    assert max(c[2] for c in centers) > 50.0
    assert meta["base_nodes"]
    assert all(len(set(m.dof_map[nid]).intersection(m._prescribed)) == 6
               for nid in meta["base_nodes"])
