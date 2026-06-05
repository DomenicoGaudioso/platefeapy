---
layout: default
title: "Casi studio - platefeapy"
nav_order: 50
has_children: true
permalink: /casestudies/
---

# Casi studio platefeapy

I casi studio raccolgono i benchmark classici della letteratura FEM per
piastre, risolti con **platefeapy** e confrontati con le soluzioni
analitiche di riferimento (Navier, Timoshenko, Levy, Roark, ecc.). Per
ogni caso viene mostrato il modello costruito, la deformata e la mappa
delle tensioni (momenti flettenti e tagli).

I casi coprono condizioni di vincolo, carichi e teorie (Mindlin vs
Kirchhoff) diverse, e mettono in evidenza sia le potenzialita' che i
limiti degli elementi Q4 a basso ordine.

## Indice dei casi

| # | Caso | Soluzione di riferimento |
|---|------|--------------------------|
| [CS01](cs01-ss-navier) | Piastra SS uniforme (Navier) | `w = 0.00406 p L⁴ / D` |
| [CS02](cs02-clamped) | Piastra incastrata uniforme | `w = 0.00126 p L⁴ / D` (Timoshenko) |
| [CS03](cs03-levy) | Piastra Levy (2 SS, 2 liberi) | Timoshenko Tab. 3 |
| [CS04](cs04-circular) | Piastra circolare (SS / incastrata) | Timoshenko §3.4 |
| [CS05](cs05-rectangular-aspect) | Piastra rettangolare - aspect ratio | Timoshenko Tab. 2 |
| [CS06](cs06-patch-load) | Piastra SS con carico parziale | Timoshenko Tab. 5 |
| [CS07](cs07-cantilever-plate) | Piastra cantilever (1 lato incastrato) | Timoshenko Tab. 30 |
| [CS08](cs08-point-load) | Piastra SS con carico concentrato | Timoshenko Tab. 4 |
| [CS09](cs09-thermal) | Piastra con gradiente termico | Curvatura imposta |
| [CS10](cs10-settlement) | Piastra SS con cedimento vincolare | Imposizione cinematica |
| [CS11](cs11-kirchhoff-vs-mindlin) | Confronto Kirchhoff vs Mindlin | thin vs thick plate |
| [CS12](cs12-patch-test) | Patch test (campo lineare) | Esatto per costruzione |

## Esecuzione

Tutti i casi studio sono eseguibili con un unico comando dalla cartella
del repository:

```bash
cd platefeapy
python -m casestudies.run_all
```

I singoli casi sono in `casestudies/csNN_*.py`; ciascuno e' eseguibile
anche standalone con `python casestudies/csNN_*.py`.

## Convenzioni

- **Mesh**: Q4 Mindlin (salvo dove indicato) con integrazione ridotta selettiva
  (SRI) per evitare lo shear locking
- **Materiale di default**: acciaio (`E = 210 GPa`, `nu = 0.3`)
- **Carico di default**: pressione uniforme `p = -1 kPa`
- **Dimensioni di default**: piastra quadrata `1 m × 1 m`, spessore `t = 10 mm`
- **Mesh tipica**: 16×16 elementi (mesh di "riferimento" usata per le figure)
- **Scala deformata**: 200× o 400× rispetto al valore reale (solo per la
  visualizzazione; i valori numerici rimangono quelli reali)

## Risultati di sintesi

| Caso | Errore FEM vs analitico | Note |
|------|-------------------------|------|
| CS01 SS Navier       | < 1%       | Convergenza monotona |
| CS02 Clamped         | < 1%       | Convergenza monotona |
| CS03 Levy quadrata   | ~40%       | Caso difficile per Q4 (mindlin shear) |
| CS04 Circolare SS    | elevato    | Mesh quadrata non ideale per cerchio |
| CS05 Aspect ratio    | < 10%      | Errore cresce per a/b << 1 |
| CS06 Patch load      | ~70%       | Errore di discretizzazione del patch |
| CS07 Cantilever      | < 10%      | Convergenza lenta vicino all'incastro |
| CS08 Point load      | < 20%      | Singolarita' al punto di carico |
| CS09 Thermal         | qualitativo | Curvatura imposta, no confronto numerico diretto |
| CS10 Settlement      | esatto     | w = -0.001 m applicato al nodo |
| CS11 Kirch/Mindlin   | diverge    | Kirchhoff ACM = thin only |
| CS12 Patch test      | < 1e-10    | Errore macchina, superato |

I casi con errore elevato sono noti nella letteratura FEM come "casi
difficili" per elementi a basso ordine. La soluzione e' usare mesh molto
fini, elementi di ordine superiore, o formulazioni arricchite (es.
assumed natural strain, mixed formulations). Per lo scopo didattico della
libreria, il confronto rimane comunque qualitativo euristico.
