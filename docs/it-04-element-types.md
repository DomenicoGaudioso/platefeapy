---
layout: default
title: "04 - Tipi di Elemento"
parent: Italiano
nav_order: 4
---

# 04 - Tipi di Elemento

platefeapy fornisce due formulazioni di elementi piastra, entrambe quadrilatere
con 4 nodi e 3 GdL per nodo (12 GdL totali per elemento).

## Mindlin-Reissner (MindlinPlateQ4)

Formulazione per **piastre spesse** che include la deformazione a taglio trasversale.

### Caratteristiche principali

- **Deformabile a taglio**: valida sia per piastre spesse che sottili
- **Integrazione SRI** (Selective Reduced Integration): 2×2 Gauss per flessione, 1×1 per taglio — evita il shear locking nelle piastre sottili
- **Funzioni di forma bilineari**: interpolazione Q4 standard
- **3 GdL per nodo**: `[w, θx, θy]`

### Quando usarlo

- Uso generale: funziona per qualsiasi rapporto di spessore `t/L`
- Piastre spesse (`t/L > 0.05`): la deformazione a taglio è significativa
- Scelta predefinita per la maggior parte delle applicazioni

### Matrice di rigidezza

La rigidezza è suddivisa in contributi flessionali e di taglio:

```
K = K_flessione (2×2 Gauss) + K_taglio (1×1 Gauss)
```

L'integrazione ridotta sulla parte di taglio previene il noto fenomeno del
**shear locking** che affligge gli elementi Mindlin standard per piastre sottili.

```python
m.add_plate(id, nodi, mat, sec, theory="mindlin")
```

## Kirchhoff-Love (KirchhoffPlateQ4)

Formulazione per **piastre sottili** che trascura la deformazione a taglio trasversale.

### Caratteristiche principali

- **Senza deformazione a taglio**: valida solo per piastre sottili (`t/L < 0.05`)
- **Elemento ACM** (Adini-Clough-Melosh): campo di spostamento cubico incompleto
- **Nessun shear locking**: intrinsecamente libero dal problema del locking
- **3 GdL per nodo**: `[w, θx, θy]`

### Quando usarlo

- Solo piastre sottili (`t/L < 0.05`)
- Quando la deformazione a taglio è trascurabile
- Leggermente più veloce di Mindlin (nessuna integrazione di taglio)

### Limitazione

L'elemento ACM assume una geometria **rettangolare**. Per quadrilateri non
rettangolari, l'elemento usa semi-dimensioni medie come approssimazione.

```python
m.add_plate(id, nodi, mat, sec, theory="kirchhoff")
```

## Confronto

| Caratteristica | Mindlin (SRI) | Kirchhoff (ACM) |
|----------------|---------------|-----------------|
| Intervallo spessore | Qualsiasi | Solo sottile (t/L < 0.05) |
| Deformazione a taglio | Sì | No |
| Shear locking | Evitato da SRI | Non applicabile |
| Geometria non rettangolare | Esatta | Approssimata |
| Integrazione | 2×2 + 1×1 | 3×3 |
| GdL per elemento | 12 | 12 |

## Studio di convergenza

Per una piastra quadrata semplicemente appoggiata (L=1m, t=10mm, p=1kPa):

| Mesh | Errore Mindlin | Errore Kirchhoff |
|------|----------------|------------------|
| 2×2 | ~15% | ~20% |
| 4×4 | ~5% | ~8% |
| 8×8 | ~1.5% | ~2% |
| 16×16 | ~0.4% | ~0.5% |

Entrambi gli elementi convergono alla soluzione analitica di Navier `w = 0.00406·p·L⁴/D`.
