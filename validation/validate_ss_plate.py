"""Validazione: piastra SS, convergenza vs soluzione analitica."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from platefeapy import Model, Material, ShellSection

L = 1.0
p = -1000.0
E = 210e9
nu = 0.3
t = 0.01
D = E * t**3 / (12.0 * (1.0 - nu**2))
w_exact = 0.00406 * abs(p) * L**4 / D

print("Validazione piastra SS (Mindlin Q4 con SRI)")
print(f"w_esatto = {w_exact:.6e}")
print(f"{'Mesh':>8s}  {'w_max FEM':>12s}  {'errore %':>10s}")

for n_el in [2, 4, 6, 8, 10, 12, 16, 20]:
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
    err = abs(w_max - w_exact) / w_exact * 100

    print(f"{n_el:4d}x{n_el:<4d}  {w_max:12.6e}  {err:10.4f}")
