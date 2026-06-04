---
layout: default
title: "14 - Esempi d'Uso"
parent: Italiano
nav_order: 14
---

# 14 - Esempi d'Uso

La directory `usage_examples/` contiene script autocontenuti che coprono tutte
le funzionalità.

## Esempi disponibili

| # | File | Descrizione |
|---|------|-------------|
| 01 | `01_convergence_ss_plate.py` | Studio di convergenza: piastra SS vs soluzione di Navier |
| 02 | `02_clamped_plate.py` | Piastra incastrata sotto pressione uniforme |
| 03 | `03_modal_analysis.py` | Analisi modale di una piastra semplicemente appoggiata |

## Esecuzione esempi

```bash
cd platefeapy
python usage_examples/01_convergence_ss_plate.py
```

## Esempio 01: Studio di convergenza

Piastra quadrata semplicemente appoggiata (L=1m, t=10mm, p=1kPa) con
raffinamento progressivo della mesh:

```python
from platefeapy import Model, Material, ShellSection

L = 1.0
p = -1000.0
E = 210e9
nu = 0.3
t = 0.01

for n_el in [2, 4, 8, 12, 16]:
    m = Model()
    # ... creare mesh con n_el × n_el elementi ...
    # ... applicare condizioni al contorno SS ...
    # ... applicare pressione uniforme ...
    res = m.solve()
    w_max = max(abs(res.displacement(nid, "w")) for nid in m.nodes)
    # ... confrontare con soluzione analitica ...
```

Output atteso:

```
Mesh  2x 2  |  w_max = 3.85e-05  |  esatto = 4.06e-05  |  err = 5.17%
Mesh  4x 4  |  w_max = 4.00e-05  |  esatto = 4.06e-05  |  err = 1.48%
Mesh  8x 8  |  w_max = 4.04e-05  |  esatto = 4.06e-05  |  err = 0.49%
Mesh 12x12  |  w_max = 4.05e-05  |  esatto = 4.06e-05  |  err = 0.22%
Mesh 16x16  |  w_max = 4.06e-05  |  esatto = 4.06e-05  |  err = 0.12%
```

## Esempio 02: Piastra incastrata

Tutti i bordi incastrati (w=0, θx=0, θy=0):

```python
for nid in nodi_bordo:
    m.fix(nid)    # tutti e 3 i GdL
```

Soluzione analitica: `w_max = 0.00126 · p · L⁴ / D`

## Esempio 03: Analisi modale

Frequenze naturali di una piastra semplicemente appoggiata confrontate con la
soluzione analitica di Navier:

```python
mr = m.modal(n_modes=6)

# Frequenze analitiche
f_mn = (π / (2·L²)) · √(D / (ρ·t)) · (m² + n²)
```

## Esempi base

La directory `examples/` contiene script più semplici:

| File | Descrizione |
|------|-------------|
| `ex01_simply_supported.py` | Piastra SS con pressione uniforme |
| `ex02_clamped.py` | Piastra incastrata con pressione uniforme |
| `ex03_point_load.py` | Piastra con carico concentrato |

```bash
python examples/ex01_simply_supported.py
```
