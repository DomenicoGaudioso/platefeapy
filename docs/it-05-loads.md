---
layout: default
title: "05 - Carichi"
parent: Italiano
nav_order: 5
---

# 05 - Carichi

platefeapy supporta tutti i principali tipi di carico per l'analisi statica di
strutture a piastra.

## Carichi di pressione

Pressione uniforme sulle superfici degli elementi (positiva verso +Z):

```python
# Pressione uniforme su un elemento
m.add_pressure(elem, p=-1000.0)       # 1 kPa verso il basso

# Applicare a tutti gli elementi
for eid in m.elements:
    m.add_pressure(eid, p=-5000.0)
```

La pressione viene convertita in forze nodali equivalenti tramite integrazione numerica:

```
f_i = ∫ N_i · p dA
```

### Carico a chiazza (pressione parziale)

```python
# Pressione su una porzione dell'elemento (coordinate naturali [-1,1]²)
m.add_patch_load(elem, p=-2000.0,
                 xi_range=(-0.5, 0.5),
                 eta_range=(-0.5, 0.5))
```

## Carichi nodali

Forze e momenti applicati direttamente ai nodi (sistema globale):

```python
m.add_nodal_load(nodo, Fz=-10000, Mx=0, My=500, case="G")
```

| Parametro | Descrizione |
|-----------|-------------|
| `Fz` | Forza trasversale [N] (positiva +Z) |
| `Mx` | Momento attorno all'asse X globale [Nm] |
| `My` | Momento attorno all'asse Y globale [Nm] |

## Carichi termici

Gradiente di temperatura attraverso lo spessore della piastra:

```python
# Differenza di temperatura tra superficie superiore e inferiore
m.add_thermal_load(elem, dT=30.0)
```

Il gradiente termico produce curvatura:

```
κ = α · ΔT / t
```

dove `α` è il coefficiente di dilatazione termica e `t` è lo spessore.
Il momento termico risultante è:

```
M_termico = D · (1 + ν) · κ
```

Questo momento viene applicato come forze nodali equivalenti.

## Cedimenti

Spostamenti o rotazioni imposte ai nodi:

```python
m.add_settlement(nodo, "w", -0.005)        # cedimento verticale 5 mm
m.add_settlement(nodo, "theta_x", 0.001)   # rotazione imposta
```

Il GdL può essere: `w`, `theta_x`, `theta_y`.

## Assegnazione ai Casi di Carico

Ogni carico può avere un `case`:

```python
m.add_pressure(1, p=-5000.0, case="G")          # permanente
m.add_nodal_load(5, Fz=-20000, case="Q")         # variabile
m.add_thermal_load(2, dT=20.0, case="T")          # termico

m.load_cases()                    # → ['G', 'Q', 'T']
res = m.solve(cases=["G", "Q"])    # combinazione
res = m.solve(cases="G")           # singolo caso
res = m.solve()                     # tutti i carichi
```

## Combinazioni con coefficienti

```python
res = m.solve(cases={"G": 1.35, "Q": 1.5})        # combinazione SLU
res = m.solve(cases={"G": 1.0, "Q": 0.3})          # combinazione SLE
```

Tutti i risultati (spostamenti, reazioni, forze interne) rispettano i coefficienti.

## Esempi illustrati

**Piastra semplicemente appoggiata sotto pressione uniforme:**

```python
m = Model()
# ... creare mesh ...
for eid in m.elements:
    m.add_pressure(eid, p=-1000.0)
for nid in nodi_bordo:
    m.fix(nid, ["w"])
res = m.solve()
```

**Piastra incastrata con carico concentrato:**

```python
m.add_nodal_load(nodo_centro, Fz=-50000.0)
for nid in nodi_bordo:
    m.fix(nid)    # tutti e 3 i GdL
```

Vedi [Esempi d'Uso](it-14-usage-examples.md) per script completi.
