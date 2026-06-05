---
layout: default
title: "CS04 - Piastra circolare (SS / incastrata)"
parent: Casi studio - platefeapy
nav_order: 54
permalink: /casestudies/cs04-circular/
---

# CS04 - Piastra circolare con mesh mappata

## Caso di letteratura

Piastra circolare di raggio `R = 1 m`, soggetta a pressione uniforme,
vincolata in due modi:

- **SS** sul bordo: solo `w = 0`
- **Incastrata** sul bordo: `w = 0`, `theta_x = 0`, `theta_y = 0`

Soluzione in coordinate polari, come riportato nei casi classici di
Timoshenko e Woinowsky-Krieger:

$$
w_\max^{SS} = \frac{(3+\nu)\, p\, R^4}{64 (1-\nu) D}
\qquad
w_\max^{clamped} = \frac{p\, R^4}{64\, D}
$$

## Mesh generica

Il caso non usa piu' una griglia rettangolare tagliata. La mesh nasce da una
griglia logica Q4 mappata direttamente nel disco tramite una trasformazione
quadrato-disco concentrica. Tutti gli elementi appartengono alla piastra e il
bordo esterno e' il cerchio discretizzato.

```python
x, y = square_to_disk(a, b, R)
m.add_node(nid, x, y)
m.add_plate(eid, [n1, n2, n3, n4], mat, sec)
```

## Visualizzazione

| Mesh | Deformata (scala 400x) |
|------|------------------------|
| ![Mesh](images/cs04_mesh_ss_32.png) | ![Deformata SS](images/cs04_deformed_ss_32.png) |

| Vincoli | Reazioni |
|---------|----------|
| ![Vincoli](images/cs04_supports_ss_32.png) | ![Reazioni](images/cs04_reactions_ss_32.png) |

## Risultati

| BC | w_max esatto | w_max FEM (32x32) | err % |
|----|--------------|-------------------|-------|
| SS (w=0) | 3.8304e-03 | 3.2580e-03 | 14.94% |
| Incastrata | 8.1250e-04 | 7.7166e-04 | 5.03% |

## Momenti flettenti

| Mx | My |
|----|----|
| ![Mx](images/cs04_Mx_ss_32.png) | ![My](images/cs04_My_ss_32.png) |

## Discussione

La nuova mesh elimina il rettangolo esterno e migliora nettamente il caso SS
rispetto al vecchio ritaglio su griglia cartesiana. Resta una discrepanza
residua dovuta all'uso di soli elementi Q4 rettilinei e alla rappresentazione
del bordo circolare con lati poligonali. Il caso incastrato converge meglio
perche' il bordo ha anche le rotazioni bloccate.

## Script

`casestudies/cs04_circular.py`
