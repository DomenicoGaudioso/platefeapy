---
layout: default
title: "06 - Vincoli"
parent: Italiano
nav_order: 6
---

# 06 - Vincoli e Condizioni al Contorno

## Tipi di vincolo

### Incastro

Tutti e 3 i GdL vincolati: `w = 0`, `θx = 0`, `θy = 0`.

```python
m.fix(nodo)
```

Uso tipico: bordi incastrati, appoggi fissi.

### Appoggio semplice

Solo spostamento trasversale vincolato: `w = 0`, rotazioni libere.

```python
m.pin(nodo)
```

Uso tipico: bordi semplicemente appoggiati.

### Vincolo personalizzato

Vincolo selettivo dei GdL:

```python
m.support(nodo, w=True, theta_x=True, theta_y=False)
```

## Condizioni al contorno comuni

| Condizione | Codice | Significato fisico |
|------------|--------|-------------------|
| Incastro | `m.fix(n)` | w=0, θx=0, θy=0 |
| Appoggio | `m.pin(n)` | w=0 |
| Simmetria (x=cost) | `m.support(n, theta_y=True)` | θy=0 |
| Simmetria (y=cost) | `m.support(n, theta_x=True)` | θx=0 |
| Guidato | `m.support(n, theta_x=True, theta_y=True)` | θx=0, θy=0, w libero |
| Libero | (niente) | Nessun vincolo |

## Condizioni di simmetria

Per una piastra con simmetria rispetto all'asse X (a y=0):

```python
for nid in nodi_simmetria:
    m.support(nid, theta_x=True)
```

Per simmetria rispetto all'asse Y (a x=0):

```python
for nid in nodi_simmetria:
    m.support(nid, theta_y=True)
```

Per doppia simmetria (modello a un quarto):

```python
m.support(nodo_angolo, theta_x=True, theta_y=True)
```

## Cedimenti

Spostamenti imposti (valori prescritti non nulli):

```python
m.add_settlement(nodo, "w", -0.005)        # 5 mm verso il basso
m.add_settlement(nodo, "theta_x", 0.001)   # rotazione imposta
```

I cedimenti vengono applicati durante la fase di soluzione e influenzano il
vettore dei carichi.

## Requisiti di stabilità

Il modello deve avere vincoli sufficienti a prevenire moti rigidi:

- **Minimo**: almeno 3 nodi non allineati con `w` vincolato
- **Raccomandato**: condizioni al contorno appropriate su tutti i bordi

Se la matrice di rigidezza è singolare, `solve()` genera un `ValueError`.
