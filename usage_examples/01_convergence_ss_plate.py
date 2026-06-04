"""Piastra quadrata semplicemente appoggiata con carico uniforme.

Confronto con la soluzione analitica di Navier:
    w_max = 0.00406 * p * L^4 / D
dove D = E t^3 / (12(1-nu^2)).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from platefeapy import Model, Material, ShellSection

L = 1.0
p = -1000.0
E = 210e9
nu = 0.3
t = 0.01

for n_el in [2, 4, 8, 12, 16]:
    m = Model()
    n = n_el + 1
    nid = 1
    for j in range(n):
        for i in range(n):
            m.add_node(nid, i * L / n_el, j * L / n_el)
            nid += 1

    mat = Material(E=E, nu=nu)
    sec = ShellSection(t=t)

    eid = 1
    for j in range(n_el):
        for i in range(n_el):
            n1 = j * n + i + 1
            n2 = n1 + 1
            n3 = n2 + n
            n4 = n1 + n
            m.add_plate(eid, [n1, n2, n3, n4], mat, sec)
            eid += 1

    for j in range(n):
        for i in range(n):
            nid = j * n + i + 1
            on_edge_x = (i == 0 or i == n_el)
            on_edge_y = (j == 0 or j == n_el)
            if on_edge_x or on_edge_y:
                m.fix(nid, ["w"])

    for eid in m.elements:
        m.add_pressure(eid, p)

    res = m.solve()

    w_max = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
    D = E * t**3 / (12.0 * (1.0 - nu**2))
    w_exact = 0.00406 * abs(p) * L**4 / D
    err = abs(w_max - w_exact) / w_exact * 100

    print(f"Mesh {n_el:2d}x{n_el:2d}  |  w_max = {w_max:.6e}  |  "
          f"esatto = {w_exact:.6e}  |  err = {err:.2f}%")
