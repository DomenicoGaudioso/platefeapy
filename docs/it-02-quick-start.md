---
layout: default
title: "02 - Quick Start"
parent: Italiano
nav_order: 2
---

# 02 - Quick Start

Il primo modello: una piastra quadrata semplicemente appoggiata sotto pressione uniforme.

```python
from platefeapy import Model, Material, ShellSection

# 1. Creare il modello
m = Model()

# 2. Aggiungere i nodi (mesh 2×2 su piastra 1×1 m)
m.add_node(1, 0.0, 0.0)
m.add_node(2, 0.5, 0.0)
m.add_node(3, 1.0, 0.0)
m.add_node(4, 0.0, 0.5)
m.add_node(5, 0.5, 0.5)
m.add_node(6, 1.0, 0.5)
m.add_node(7, 0.0, 1.0)
m.add_node(8, 0.5, 1.0)
m.add_node(9, 1.0, 1.0)

# 3. Definire materiale e sezione
mat = Material(E=210e9, nu=0.3)       # acciaio
sec = ShellSection(t=0.01)             # spessore 10 mm

# 4. Aggiungere elementi piastra (4 quadrilateri)
m.add_plate(1, [1, 2, 5, 4], mat, sec)
m.add_plate(2, [2, 3, 6, 5], mat, sec)
m.add_plate(3, [4, 5, 8, 7], mat, sec)
m.add_plate(4, [5, 6, 9, 8], mat, sec)

# 5. Bordi semplicemente appoggiati (w=0 sui nodi di bordo)
for nid in [1, 2, 3, 4, 6, 7, 8, 9]:
    m.fix(nid, ["w"])

# 6. Applicare pressione uniforme
for eid in m.elements:
    m.add_pressure(eid, p=-1000.0)    # 1 kPa verso il basso

# 7. Risolvere
res = m.solve()

# 8. Leggere i risultati
print(res.displacements(5))   # [w, theta_x, theta_y] al centro
```

## Risultato atteso

Per una piastra quadrata semplicemente appoggiata sotto pressione uniforme:

```
w_max ≈ 0.00406 · p · L⁴ / D
```

dove `D = E·t³ / (12·(1−ν²))` è la rigidezza flessionale.

```python
D = 210e9 * 0.01**3 / (12 * (1 - 0.3**2))
w_exact = 0.00406 * 1000 * 1.0**4 / D
print(f"w_max FEM   = {abs(res.displacement(5, 'w')):.6e} m")
print(f"w_max esatto = {w_exact:.6e} m")
```

## Prossimi passi

- [Modello Strutturale](it-03-structural-model.md) — nodi, materiali, sezioni, elementi
- [Tipi di Elemento](it-04-element-types.md) — Mindlin vs Kirchhoff
- [Carichi](it-05-loads.md) — pressione, nodali, termici, cedimenti
- [Post-Processing](it-08-post-processing.md) — momenti, taglio, spostamenti
