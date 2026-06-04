"""Analisi modale di una piastra semplicemente appoggiata.

Confronto frequenze con la soluzione analitica di Navier:
    f_mn = (pi / (2 L^2)) * sqrt(D / (rho * t)) * (m^2 + n^2)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from platefeapy import Model, Material, ShellSection

L = 1.0
E = 210e9
nu = 0.3
t = 0.01
rho = 7850.0

n_el = 8
m = Model()
n = n_el + 1
nid = 1
for j in range(n):
    for i in range(n):
        m.add_node(nid, i * L / n_el, j * L / n_el)
        nid += 1

mat = Material(E=E, nu=nu, rho=rho)
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

modal = m.modal(n_modes=6)

D = E * t**3 / (12.0 * (1.0 - nu**2))
mass_per_area = rho * t

print("Analisi modale piastra SS")
print(f"{'Modo':>4s}  {'f FEM [Hz]':>12s}  {'f analitica [Hz]':>18s}  {'err %':>8s}")
modes_analytical = [(1, 1), (1, 2), (2, 1), (2, 2), (1, 3), (3, 1)]
for k in range(min(6, len(modal.freq))):
    f_fem = modal.freq[k]
    if k < len(modes_analytical):
        mm, nn = modes_analytical[k]
        f_exact = (np.pi / (2 * L**2)) * np.sqrt(D / mass_per_area) * (mm**2 + nn**2)
        err = abs(f_fem - f_exact) / f_exact * 100
        print(f"{k+1:4d}  {f_fem:12.3f}  {f_exact:18.3f}  {err:8.2f}")
    else:
        print(f"{k+1:4d}  {f_fem:12.3f}")
