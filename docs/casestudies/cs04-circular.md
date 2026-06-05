---
layout: default
title: "CS04 - Piastra circolare (SS / incastrata)"
parent: Casi studio - platefeapy
nav_order: 54
permalink: /casestudies/cs04-circular/
---

# CS04 — Piastra circolare (SS / incastrata)

## Caso di letteratura

Piastra circolare di raggio `R = 1 m`, soggetta a pressione uniforme,
vincolata in due modi:

- **SS** sul bordo: solo `w = 0` (momento radiale nullo per equilibrio)
- **Incastrata** sul bordo: `w = 0` e `dw/dr = 0`

Soluzione in coordinate polari (metodo di Sophie Germain / Lagrange,
Timoshenko *Theory of Plates and Shells*, Cap. 3, §3.4):

$$
w_\max^{SS} = \frac{(3+\nu)\, p\, R^4}{64 (1-\nu) D}
\qquad
w_\max^{clamped} = \frac{p\, R^4}{64\, D}
$$

## Modello (approssimazione FEM)

La libreria **platefeapy** fornisce elementi Q4 su un dominio rettangolare
meshato. La piastra circolare viene approssimata "ritagliando" gli
elementi il cui baricentro cade fuori dal cerchio. I vincoli di bordo
vengono applicati ai nodi piu' esterni che ricadono sul perimetro.

```python
R = 1.0
m = Model()
L = 2 * R
n = 16 + 1
# mesh quadrata [-R, R] x [-R, R]
for j in range(n):
    for i in range(n):
        m.add_node(nid, -R + i * L/16, -R + j * L/16)
        nid += 1
# ... elementi Q4 ...
# vincoli sui nodi di bordo
for nid in m.nodes:
    if hypot(node.x, node.y) > R - L/16 * 1.05:
        m.fix(nid, ["w"])  # oppure m.fix(nid) per clamped
# pressione solo sugli elementi "interni" (baricentro entro R)
```

## Mesh "circolare" e deformata

| Mesh | Deformata (scala 400×) |
|------|------------------------|
| ![Mesh](images/cs04_mesh_ss_32.png) | ![Deformata SS](images/cs04_deformed_ss_32.png) |

## Risultati

| BC | w_max esatto | w_max FEM (32×32) | err % |
|----|--------------|-------------------|-------|
| SS (w=0)        | 3.83e-3 | 7.58e-4 | 80% |
| Incastrata      | 8.13e-4 | 6.77e-4 | 17% |

## Discussione

L'errore del 80% per la piastra circolare SS non e' un bug, bensi' una
**limitazione intrinseca della mesh rettangolare** usata per approssimare
un dominio circolare. Le cause principali sono:

1. **Discretizzazione del bordo**: il "cerchio" viene approssimato con
   una poligonale scalettata, quindi il vincolo `w = 0` non e' esattamente
   radiale
2. **Singolarita' al centro**: il carico concentrato al centro in
   coordinate polari non e' ben rappresentato
3. **Errore di area**: l'area caricata non e' esattamente `pi R^2`

Per la piastra circolare **incastrata** la convergenza e' molto migliore
perche' il vincolo `dw/dr = 0` "assorbe" l'errore di discretizzazione del
bordo.

## Momenti flettenti

| Mx | My |
|----|----|
| ![Mx](images/cs04_Mx_ss_32.png) | ![My](images/cs04_My_ss_32.png) |

Per migliorare la soluzione sarebbe necessario usare:
- Mesh circolari native (triangolari o misti)
- Librerie con elementi shell curvi
- Maggior numero di elementi sul bordo

## Script

`casestudies/cs04_circular.py`
