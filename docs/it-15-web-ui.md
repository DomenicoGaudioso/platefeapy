---
layout: default
title: "15 - Interfaccia Web"
parent: Italiano
nav_order: 15
---

# 15 - Interfaccia Web (Streamlit)

platefeapy include un'applicazione web Streamlit per l'analisi interattiva di piastre.

## Installazione

```bash
pip install platefeapy streamlit plotly
```

## Avvio

```bash
streamlit run app.py
```

L'app si apre nel browser predefinito a `http://localhost:8501`.

## Layout dell'interfaccia

L'interfaccia web ha tre tab:

### Modello

Definire il modello di piastra attraverso tabelle modificabili:

- **Nodi**: ID nodo, coordinate X, Y
- **Materiali**: nome materiale, E, nu, alpha, rho
- **Sezioni**: nome sezione, spessore t, fattore di taglio kappa
- **Elementi**: ID elemento, ID nodi (N1-N4), materiale, sezione, teoria
- **Vincoli**: ID nodo, W, Rx, Ry (checkbox booleane)
- **Carichi nodali**: ID nodo, Fz, Mx, My, Caso
- **Pressioni**: ID elemento, pressione p, Caso

Cliccare **Applica modifiche** per ricostruire il modello.

### Analisi

Scegliere il tipo di analisi:

- **Statica**: risolvere il problema statico
- **Modale**: calcolare frequenze naturali e forme modali

Opzioni:
- Solver sparso (per modelli grandi)
- Numero di modi (per analisi modale)

### Risultati

Visualizzare i risultati:

- **Deformata**: forma deformata 3D con fattore di scala
- **Mappe a colori**: Mx, My, Mxy, Qx, Qy, w
- **Spostamenti nodali**: tabella di [w, θx, θy] per nodo
- **Forme modali**: visualizzazione 3D di ogni modo
- **Tabella frequenze**: frequenze naturali e periodi

## Flusso di lavoro esempio

1. **Definire nodi**: creare una griglia 4×4 (25 nodi)
2. **Aggiungere materiale**: E=210e9, nu=0.3
3. **Aggiungere sezione**: t=0.01
4. **Creare elementi**: 16 piastre quadrilatere
5. **Applicare vincoli**: bordi semplicemente appoggiati (W=1 sul bordo)
6. **Applicare pressione**: p=-1000 su tutti gli elementi
7. **Eseguire analisi statica**
8. **Visualizzare risultati**: forma deformata, contorni dei momenti

## Screenshot

L'interfaccia web fornisce:
- Visualizzazione 3D interattiva (rotazione, zoom, pan)
- Tabelle modificabili con aggiunta/rimozione righe
- Anteprima del modello in tempo reale
- Capacità di esportazione (pianificato)

## Limitazioni

- Nessun import Excel (pianificato)
- Nessun export HDF5 (pianificato)
- Limitato alle funzionalità disponibili nell'API Python

## Accesso programmatico

L'interfaccia web usa la stessa API Python della libreria:

```python
from platefeapy import Model, Material, ShellSection

# L'interfaccia web costruisce questo modello dalle tabelle
m = Model()
# ... aggiungere nodi, elementi, carichi ...
res = m.solve()
```
