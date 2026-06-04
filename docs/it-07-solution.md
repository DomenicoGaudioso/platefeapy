---
layout: default
title: "07 - Soluzione"
parent: Italiano
nav_order: 7
---

# 07 - Soluzione

## Soluzione base

```python
res = m.solve()
```

Restituisce un oggetto `Result` contenente spostamenti, reazioni e forze degli elementi.

## Combinazioni di casi di carico

### Tutti i carichi (default)

```python
res = m.solve()    # tutti i carichi con coefficiente 1
```

### Singolo caso di carico

```python
res = m.solve(cases="G")    # solo carichi con case="G"
```

### Casi multipli (somma)

```python
res = m.solve(cases=["G", "Q"])    # G + Q (entrambi con coefficiente 1)
```

### Combinazione con coefficienti

```python
res = m.solve(cases={"G": 1.35, "Q": 1.5})    # 1.35·G + 1.5·Q (SLU)
res = m.solve(cases={"G": 1.0, "Q": 0.3})      # 1.0·G + 0.3·Q (SLE)
```

Tutti i risultati (spostamenti, reazioni, momenti, tagli) sono scalati linearmente
dai coefficienti.

## Opzioni del solver

### Solver denso (default)

```python
res = m.solve(sparse=False)
```

Usa `numpy.linalg.solve` con assemblaggio completo della matrice. Adatto per
modelli piccoli e medi (< 10.000 GdL).

### Solver sparso

```python
res = m.solve(sparse=True)
```

Usa `scipy.sparse.linalg.spsolve` con assemblaggio sparso. Raccomandato per
modelli grandi (> 5.000 elementi).

## Metodi di assemblaggio

### Matrice di rigidezza

```python
K = m.assemble_stiffness()    # densa (ndof × ndof)
```

### Vettore dei carichi

```python
F = m.assemble_loads()                    # tutti i carichi
F = m.assemble_loads(cases={"G": 1.35})   # con coefficienti
```

## Oggetto Result

```python
res = m.solve()

# Spostamenti nodali
res.displacements(nodo)           # array [w, theta_x, theta_y]
res.displacement(nodo, "w")       # singolo GdL (float)

# Reazioni nodali
res.reactions(nodo)               # array [Fz, Mx, My]

# Forze degli elementi
res.element_forces[elem_id]       # vettore 12×1 (forze nodali in coord. locali)

# Array grezzi
res.U                             # vettore spostamenti globali (ndof,)
res.R                             # vettore reazioni globali (ndof,)
```

## Gestione errori

```python
try:
    res = m.solve()
except ValueError as e:
    if "labile" in str(e):
        print("Vincoli insufficienti: aggiungere più supporti")
    elif "singolare" in str(e):
        print("Matrice singolare: verificare la qualità della mesh")
```

Errori comuni:
- **"Nessun vincolo: struttura labile"** — nessun vincolo definito
- **"Matrice singolare"** — vincoli insufficienti o mesh degenere
