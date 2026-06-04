"""Esempio: piastra con carico concentrato."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from platefeapy import Model, Material, ShellSection

L = 2.0
n_el = 4

m = Model()
n = n_el + 1
nid = 1
for j in range(n):
    for i in range(n):
        m.add_node(nid, i * L / n_el, j * L / n_el)
        nid += 1

mat = Material(E=30e9, nu=0.2)
sec = ShellSection(t=0.15)

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

center_node = (n_el // 2) * n + (n_el // 2) + 1
m.add_nodal_load(center_node, Fz=-50000.0)

res = m.solve()
w_center = res.displacement(center_node, "w")
print(f"Piastra con carico concentrato P=50 kN al centro")
print(f"w_centro = {w_center:.6e} m")
