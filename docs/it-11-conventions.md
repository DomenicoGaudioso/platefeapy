---
layout: default
title: "11 - Convenzioni"
parent: Italiano
nav_order: 11
---

# 11 - Convenzioni

## Gradi di libertà nodali

Ogni nodo ha 3 GdL in ordine: `[w, theta_x, theta_y]`

- `w`: spostamento trasversale (fuori piano, direzione +Z)
- `theta_x`: rotazione attorno all'asse X globale
- `theta_y`: rotazione attorno all'asse Y globale

## Geometria della piastra

- **Piano della piastra**: X-Y globale
- **Spessore**: direzione Z (fuori piano)
- **Pressione positiva**: verso +Z (verso l'alto)

## Ordinamento nodi dell'elemento

I nodi devono essere ordinati in senso **antiorario** visti da +Z:

```
  4 --- 3
  |     |
  1 --- 2
```

## Convenzione dei segni dei momenti

- **Mx**: momento flettente che causa curvatura in direzione X (attorno all'asse Y)
- **My**: momento flettente che causa curvatura in direzione Y (attorno all'asse X)
- **Mxy**: momento torcente

Momenti positivi causano trazione sulla superficie inferiore (lato −Z).

## Convenzione dei segni delle forze di taglio

- **Qx**: forza di taglio in direzione X
- **Qy**: forza di taglio in direzione Y

Positive nella direzione positiva dell'asse corrispondente.

## Unità di misura

Il sistema è **agnostico rispetto alle unità**: l'utente sceglie le unità purché
siano coerenti.

| Grandezza | Unità SI |
|-----------|----------|
| Lunghezza | m |
| Spessore | m |
| Forza | N |
| Pressione | Pa (N/m²) |
| Momento | Nm/m (per unità di lunghezza) |
| Temperatura | °C |
| Densità | kg/m³ |

## Coordinate naturali

L'integrazione dell'elemento usa coordinate naturali `(ξ, η)` in `[-1, 1]²`:

| Punto | ξ | η |
|-------|---|---|
| Nodo 1 | -1 | -1 |
| Nodo 2 | +1 | -1 |
| Nodo 3 | +1 | +1 |
| Nodo 4 | -1 | +1 |
| Centro | 0 | 0 |

## Rigidezza flessionale

```
D = E · t³ / (12 · (1 − ν²))
```

## Rigidezza al taglio

```
Ds = κ · G · t
```

dove `κ = 5/6` è il fattore di correzione al taglio per piastre di Mindlin.
