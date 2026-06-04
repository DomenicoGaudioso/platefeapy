---
layout: default
title: "03 - Modello Strutturale"
parent: Italiano
nav_order: 3
---

# 03 - Modello Strutturale

## Nodi

Ogni nodo ha 3 gradi di libertà (GdL): `[w, theta_x, theta_y]`.

```python
m.add_node(id, x, y)   # id = identificativo intero, coordinate in metri
```

Esempio:
```python
m.add_node(1, 0, 0)    # origine
m.add_node(2, 5, 0)    # 5 m lungo X
m.add_node(3, 5, 3)    # 5 m in X, 3 m in Y
m.add_node(4, 0, 3)    # angolo
```

## Materiali

```python
mat = Material(E=210e9, nu=0.3, alpha=1.2e-5)   # acciaio
mat = Material(E=30e9, nu=0.2, alpha=1.0e-5)       # calcestruzzo
```

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `E` | Modulo di Young [Pa] | richiesto |
| `nu` | Coefficiente di Poisson | 0.3 |
| `alpha` | Coefficiente di dilatazione termica [1/°C] | 0.0 |
| `G` | Modulo di taglio [Pa] | calcolato da E e nu |
| `rho` | Densità [kg/m³] | 0.0 |

## Sezioni

```python
sec = ShellSection(t=0.01)              # piastra 10 mm
sec = ShellSection(t=0.20, kappa=5/6)   # 200 mm con correzione al taglio
```

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `t` | Spessore della piastra [m] | richiesto |
| `kappa` | Fattore di correzione al taglio | 5/6 |

### Proprietà derivate

```python
D = sec.D_bending(E, nu)     # rigidezza flessionale: E·t³/(12·(1−ν²))
Ds = sec.D_shear(G)           # rigidezza al taglio: κ·G·t
C = sec.D_membrane(E, nu)    # rigidezza membranale: E·t/(1−ν²)
```

## Elementi

### Aggiungere un elemento piastra

```python
m.add_plate(id, [n1, n2, n3, n4], materiale, sezione, theory="mindlin")
```

I nodi devono essere ordinati in senso **antiorario** visti da +Z:

```
  4 --- 3
  |     |
  1 --- 2
```

### Teorie degli elementi

| Teoria | Keyword | Descrizione |
|--------|---------|-------------|
| Mindlin-Reissner | `"mindlin"` | Piastre spesse, deformabile a taglio, integrazione SRI |
| Kirchhoff-Love | `"kirchhoff"` | Piastre sottili, elemento ACM, senza deformazione a taglio |

Vedi [Tipi di Elemento](it-04-element-types.md) per i dettagli.

## Vincoli

```python
m.fix(nodo)                              # incastrato: tutti e 3 i GdL vincolati
m.pin(nodo)                              # appoggio semplice: solo w
m.support(nodo, w=True, theta_x=True)    # personalizzato: solo GdL specificati
```

| Metodo | GdL Vincolati | Uso tipico |
|--------|---------------|------------|
| `fix(n)` | w, theta_x, theta_y | Bordo incastrato |
| `pin(n)` | w | Bordo semplicemente appoggiato |
| `support(n,...)` | personalizzato | Simmetria, bordo guidato |

Esempi:
```python
# Bordo incastrato
m.fix(1)

# Semplicemente appoggiato (w=0, rotazioni libere)
m.pin(2)

# Simmetria: w e theta_x fissati, theta_y libero
m.support(3, w=True, theta_x=True)

# Guidato: rotazioni fissate, w libero
m.support(4, theta_x=True, theta_y=True)
```

## Soluzione

```python
res = m.solve()                   # solver denso (default)
res = m.solve(sparse=True)        # solver sparso (modelli grandi)
res = m.solve(cases=["G", "Q"])    # casi di carico specifici
```

Vedi [Soluzione](it-07-solution.md) per i dettagli.
