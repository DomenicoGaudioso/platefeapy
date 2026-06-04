---
layout: default
title: "10 - Analisi Modale"
parent: Italiano
nav_order: 10
---

# 10 - Analisi Modale

## Frequenze naturali e forme modali

```python
mr = m.modal(n_modes=6)

for i in range(len(mr.freq)):
    print(f"Modo {i+1}: f = {mr.freq[i]:.3f} Hz, T = {mr.period[i]:.3f} s")
```

`modal()` risolve il problema agli autovalori `K φ = ω² M φ` sui GdL liberi.

## Matrice di massa

La matrice di massa è **concentrata** (diagonale) e calcolata dalla densità
degli elementi:

```python
M = m.assemble_mass()    # vettore di massa diagonale (ndof,)
```

Massa per nodo:

```
m_nodo = ρ · t · A_elemento / 4
```

Inerzia rotazionale (attorno a X e Y):

```
I_rot = m_nodo · t² / 12
```

## Oggetto Result

```python
mr = m.modal(n_modes=10)

mr.omega          # pulsazioni [rad/s]
mr.freq           # frequenze naturali [Hz]
mr.period         # periodi [s]
mr.phi            # forme modali (ndof × n_modi)

# Singolo modo
mr.mode(i)                    # vettore forma modale (ndof,)
mr.mode_shape(i, nodo)        # [w, theta_x, theta_y] al nodo
```

## Visualizzazione

```python
from platefeapy.plotting import plot_mode

# Primo modo
plot_mode(mr, i=0, scale=100).show()

# Ciclo sui modi
for i in range(min(6, len(mr.freq))):
    plot_mode(mr, i=i, scale=100).show()
```

## Confronto analitico

Per una piastra rettangolare semplicemente appoggiata (a × b), la soluzione di
Navier fornisce:

```
f_mn = (π / (2·a²)) · √(D / (ρ·t)) · (m² + (a/b)²·n²)
```

dove `m, n = 1, 2, 3, ...` sono i numeri del modo.

### Esempio: piastra quadrata

```python
import numpy as np

L = 1.0
E = 210e9
nu = 0.3
t = 0.01
rho = 7850.0

D = E * t**3 / (12 * (1 - nu**2))
massa_per_area = rho * t

# Primo modo (m=1, n=1)
f_11 = (np.pi / (2 * L**2)) * np.sqrt(D / massa_per_area) * (1**2 + 1**2)
print(f"f_11 analitica = {f_11:.3f} Hz")

# Confronto con FEM
mr = m.modal(n_modes=1)
print(f"f_11 FEM        = {mr.freq[0]:.3f} Hz")
```

## Interpretazione delle forme modali

| Modo | Semplicemente appoggiata | Incastrata |
|------|--------------------------|------------|
| 1 | Mezza onda singola (1,1) | Cupola singola |
| 2 | Due mezze onde (1,2) o (2,1) | Asimmetrica |
| 3 | Armonica superiore | Pattern complesso |

## Requisiti

- Il materiale deve avere `rho > 0` (densità)
- Vincoli sufficienti a prevenire modi di corpo rigido
- I GdL liberi senza massa sono eliminati per condensazione statica

Se `rho = 0`, `modal()` genera:
```
ValueError: Massa nulla: impostare rho nel materiale.
```
