---
layout: default
title: "07 - Solution"
parent: English
nav_order: 7
---

# 07 - Solution

## Basic solution

```python
res = m.solve()
```

Returns a `Result` object containing displacements, reactions, and element forces.

## Load case combinations

### All loads (default)

```python
res = m.solve()    # all loads with coefficient 1
```

### Single load case

```python
res = m.solve(cases="G")    # only loads with case="G"
```

### Multiple cases (sum)

```python
res = m.solve(cases=["G", "Q"])    # G + Q (both with coefficient 1)
```

### Combination with coefficients

```python
res = m.solve(cases={"G": 1.35, "Q": 1.5})    # 1.35·G + 1.5·Q (ULS)
res = m.solve(cases={"G": 1.0, "Q": 0.3})      # 1.0·G + 0.3·Q (SLS)
```

All results (displacements, reactions, moments, shear forces) are linearly
scaled by the coefficients.

## Solver options

### Dense solver (default)

```python
res = m.solve(sparse=False)
```

Uses `numpy.linalg.solve` with full matrix assembly. Suitable for small to
medium models (< 10,000 DOFs).

### Sparse solver

```python
res = m.solve(sparse=True)
```

Uses `scipy.sparse.linalg.spsolve` with sparse matrix assembly. Recommended for
large models (> 5,000 elements).

## Assembly methods

### Stiffness matrix

```python
K = m.assemble_stiffness()    # dense (ndof × ndof)
```

### Load vector

```python
F = m.assemble_loads()                    # all loads
F = m.assemble_loads(cases={"G": 1.35})   # with coefficients
```

## Result object

```python
res = m.solve()

# Nodal displacements
res.displacements(node)           # array [w, theta_x, theta_y]
res.displacement(node, "w")       # single DOF (float)

# Nodal reactions
res.reactions(node)               # array [Fz, Mx, My]

# Element forces
res.element_forces[elem_id]       # 12×1 vector (nodal forces in local coords)

# Raw arrays
res.U                             # global displacement vector (ndof,)
res.R                             # global reaction vector (ndof,)
```

## Error handling

```python
try:
    res = m.solve()
except ValueError as e:
    if "labile" in str(e):
        print("Insufficient constraints: add more supports")
    elif "singular" in str(e):
        print("Singular matrix: check mesh quality")
```

Common errors:
- **"Nessun vincolo: struttura labile"** — no supports defined
- **"Matrice singolare"** — insufficient constraints or degenerate mesh
