---
layout: default
title: "13 - Test e Validazione"
parent: Italiano
nav_order: 13
---

# 13 - Test e Validazione

## Esecuzione test

```bash
pip install -e ".[dev]"
python -m pytest tests -v
```

## Copertura test

La suite di test include:

| Test | Descrizione |
|------|-------------|
| `test_simply_supported_uniform_pressure` | Piastra SS sotto carico uniforme vs soluzione di Navier |
| `test_kirchhoff_plate` | Elemento Kirchhoff ACM funzionalità base |
| `test_nodal_load` | Carico nodale concentrato |
| `test_modal_analysis` | Analisi modale (frequenze positive) |
| `test_settlement` | Spostamento imposto |
| `test_stiffness_symmetry` | Simmetria matrice K |
| `test_stiffness_positive_diagonal` | Diagonale K non negativa |

## Validazione analitica

### Piastra quadrata semplicemente appoggiata

Soluzione di Navier per pressione uniforme:

```
w_max = 0.00406 · p · L⁴ / D
```

dove `D = E·t³ / (12·(1−ν²))`.

Studio di convergenza (Mindlin Q4 con SRI):

| Mesh | w_max FEM | w_max esatto | Errore |
|------|-----------|--------------|--------|
| 2×2 | 3.85e-5 | 4.06e-5 | 5.2% |
| 4×4 | 4.00e-5 | 4.06e-5 | 1.5% |
| 8×8 | 4.04e-5 | 4.06e-5 | 0.5% |
| 16×16 | 4.05e-5 | 4.06e-5 | 0.1% |

### Piastra quadrata incastrata

Soluzione analitica:

```
w_max = 0.00126 · p · L⁴ / D
```

La convergenza è più lenta a causa del gradiente ripido vicino ai bordi incastrati.

## Script di validazione

```bash
python validation/validate_ss_plate.py
```

Questo script esegue uno studio di convergenza per la piastra semplicemente
appoggiata e stampa l'errore a ogni livello di raffinamento della mesh.

## Limitazioni note

1. **Elemento Kirchhoff ACM**: assume geometria rettangolare; quadrilateri non
   rettangolari usano semi-dimensioni medie (approssimato).

2. **Shear locking**: l'elemento Mindlin con integrazione completa soffre di
   shear locking per piastre sottili (t/L < 0.01). La tecnica SRI mitiga questo.

3. **Distorsione mesh**: elementi altamente distorti (rapporto d'aspetto > 5,
   skew > 45°) riducono l'accuratezza.

4. **Carichi concentrati**: carichi puntuali producono campi di tensione singolari;
   i risultati vicino al punto di carico dipendono dalla mesh.

## Confronto con la letteratura

L'elemento Mindlin Q4 con SRI è una formulazione standard documentata in:

- Hughes, T.J.R. (1987). *The Finite Element Method*. Prentice-Hall.
- Zienkiewicz, O.C., Taylor, R.L. (2000). *The Finite Element Method*, Vol. 2.
  Butterworth-Heinemann.

L'elemento ACM di Kirchhoff è descritto in:

- Adini, A., Clough, R.W. (1961). "Analysis of thin plates by the finite element
  method". UC Berkeley.
- Melosh, R.J. (1963). "Basis for derivation of matrices for the direct stiffness
  method". AIAA Journal.
