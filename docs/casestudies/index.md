---
layout: default
title: "Casi studio - platefeapy"
nav_order: 50
has_children: true
permalink: /casestudies/
---

# Casi studio platefeapy

I casi studio raccolgono benchmark classici della letteratura FEM per piastre,
insieme a esempi applicativi pensati per mostrare mesh generiche, vincoli,
deformate amplificate, iso-linee e mappe di momento.

## Indice dei casi

| # | Caso | Soluzione o riferimento |
|---|------|-------------------------|
| [CS01](cs01-ss-navier) | Piastra SS uniforme (Navier) | `w = 0.00406 p L^4 / D` |
| [CS02](cs02-clamped) | Piastra incastrata uniforme | `w = 0.00126 p L^4 / D` |
| [CS03](cs03-levy) | Piastra Levy (2 SS, 2 liberi) | Timoshenko Tab. 3 |
| [CS04](cs04-circular) | Piastra circolare con mesh mappata | Timoshenko, piastra circolare |
| [CS05](cs05-rectangular-aspect) | Piastra rettangolare - aspect ratio | Timoshenko Tab. 2 |
| [CS06](cs06-patch-load) | Piastra SS con carico parziale | Timoshenko Tab. 5 |
| [CS07](cs07-cantilever-plate) | Piastra cantilever (1 lato incastrato) | Timoshenko Tab. 30 |
| [CS08](cs08-point-load) | Piastra SS con carico concentrato | Timoshenko Tab. 4 |
| [CS09](cs09-thermal) | Piastra con gradiente termico | Curvatura imposta |
| [CS10](cs10-settlement) | Piastra SS con cedimento vincolare | Imposizione cinematica |
| [CS11](cs11-kirchhoff-vs-mindlin) | Confronto Kirchhoff vs Mindlin | thin vs thick plate |
| [CS12](cs12-patch-test) | Patch test (campo lineare) | Esatto per costruzione |
| [CS13](cs13-chimney) | Ciminiera rastremata con apertura | ACI 307 / CICIND |

## Esecuzione

Tutti i casi studio sono eseguibili con un unico comando dalla cartella del
repository:

```bash
python -m casestudies.run_all
```

I singoli casi sono in `casestudies/csNN_*.py`; ciascuno e' eseguibile anche
standalone con `python casestudies/csNN_*.py`.

## Convenzioni

- **Mesh**: Q4 Mindlin, salvo dove indicato.
- **Materiale di default**: acciaio (`E = 210 GPa`, `nu = 0.3`) nei benchmark.
- **Carico di default**: pressione uniforme `p = -1 kPa`, salvo casi applicativi.
- **Scala deformata**: solo grafica; le legende riportano i valori reali.
- **Iso-linee**: disponibili sulle mappe di spostamento e tensione/momento.

## Risultati di sintesi

| Caso | Errore FEM vs riferimento | Note |
|------|---------------------------|------|
| CS01 SS Navier | < 1% | Convergenza monotona |
| CS02 Clamped | < 1% | Convergenza monotona |
| CS03 Levy quadrata | ~40% | Caso difficile per Q4 |
| CS04 Circolare SS | ~15% | Mesh mappata sul disco, senza rettangolo esterno |
| CS05 Aspect ratio | < 10% | Errore cresce per a/b << 1 |
| CS06 Patch load | ~70% | Errore di discretizzazione del patch |
| CS07 Cantilever | < 10% | Convergenza lenta vicino all'incastro |
| CS08 Point load | < 20% | Singolarita' al punto di carico |
| CS09 Thermal | qualitativo | Curvatura imposta |
| CS10 Settlement | esatto | `w = -0.001 m` applicato al nodo |
| CS11 Kirch/Mindlin | diverge | Kirchhoff ACM = thin only |
| CS12 Patch test | < 1e-10 | Errore macchina |
| CS13 Ciminiera | qualitativo | Mesh generica con foro e vincoli/reazioni |

I casi con errore elevato sono noti nella letteratura FEM come casi difficili
per elementi a basso ordine. La libreria li mantiene per mostrare chiaramente
quando serve una mesh piu' fine, un elemento di ordine superiore o una
formulazione shell piu' ricca.
