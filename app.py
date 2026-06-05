# -*- coding: utf-8 -*-
"""
platefeapy — UI Streamlit
=========================

Interfaccia grafica per la libreria `platefeapy` (solutore FEM per piastre).

Avvio:
    streamlit run app.py
"""

from __future__ import annotations

import io
import os
import traceback

import numpy as np
import pandas as pd
import streamlit as st

import platefeapy as pf
from platefeapy import Material, Model, ShellSection
from platefeapy import postprocess

DOF_NAMES = ["w", "theta_x", "theta_y"]

st.set_page_config(page_title="platefeapy — UI", layout="wide", page_icon="🔲")


def _empty(cols: dict) -> pd.DataFrame:
    return pd.DataFrame({k: pd.Series(dtype=v) for k, v in cols.items()})


TABLE_SCHEMAS = {
    "nodes": {"Node": "Int64", "X": "float", "Y": "float"},
    "materials": {"Material": "string", "E": "float", "nu": "float",
                  "alpha": "float", "rho": "float"},
    "sections": {"Section": "string", "t": "float", "kappa": "float"},
    "elements": {"Element": "Int64", "N1": "Int64", "N2": "Int64",
                 "N3": "Int64", "N4": "Int64",
                 "Material": "string", "Section": "string",
                 "Theory": "string"},
    "supports": {"Node": "Int64", "W": "boolean",
                 "Rx": "boolean", "Ry": "boolean"},
    "nodal_loads": {"Node": "Int64", "Fz": "float",
                    "Mx": "float", "My": "float", "Case": "string"},
    "pressure_loads": {"Element": "Int64", "p": "float", "Case": "string"},
}


def blank_tables() -> dict:
    return {name: _empty(cols) for name, cols in TABLE_SCHEMAS.items()}


def _f(v, default=None):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return default
    if isinstance(v, str) and v.strip() == "":
        return default
    try:
        if pd.isna(v):
            return default
    except (TypeError, ValueError):
        pass
    return float(v)


def _i(v, default=None):
    f = _f(v, None)
    return default if f is None else int(round(f))


def tables_to_model(t: dict) -> Model:
    m = Model()
    node_ids = set()
    for _, r in t["nodes"].iterrows():
        nid = _i(r.get("Node"))
        if nid is None or nid in node_ids:
            continue
        m.add_node(nid, _f(r.get("X"), 0.0), _f(r.get("Y"), 0.0))
        node_ids.add(nid)
    if not node_ids:
        raise ValueError("Nessun nodo definito.")

    materials = {}
    for _, r in t["materials"].iterrows():
        name = str(r.get("Material") or "").strip()
        if not name:
            continue
        E = _f(r.get("E"))
        if E is None:
            raise ValueError(f"Materiale '{name}': E mancante.")
        materials[name] = Material(
            E=E, nu=_f(r.get("nu"), 0.3), alpha=_f(r.get("alpha"), 0.0),
            rho=_f(r.get("rho"), 0.0), name=name)

    sections = {}
    for _, r in t["sections"].iterrows():
        sid = str(r.get("Section") or "").strip()
        if not sid:
            continue
        sec = ShellSection(t=_f(r.get("t"), 0.1),
                           kappa=_f(r.get("kappa"), 5 / 6))
        m.sections = getattr(m, "sections", {})
        sections[sid] = sec

    elem_ids = set()
    for _, r in t["elements"].iterrows():
        eid = _i(r.get("Element"))
        if eid is None or eid in elem_ids:
            continue
        ns = [_i(r.get(f"N{i}")) for i in range(1, 5)]
        if any(n is None or n not in node_ids for n in ns):
            continue
        mname = str(r.get("Material") or "").strip()
        sname = str(r.get("Section") or "").strip()
        if mname not in materials or sname not in sections:
            continue
        theory = str(r.get("Theory") or "mindlin").strip().lower()
        m.add_plate(eid, ns, materials[mname], sections[sname], theory=theory)
        elem_ids.add(eid)

    for _, r in t["supports"].iterrows():
        nid = _i(r.get("Node"))
        if nid is None or nid not in node_ids:
            continue
        flags = {}
        if bool(r.get("W")):
            flags["w"] = True
        if bool(r.get("Rx")):
            flags["theta_x"] = True
        if bool(r.get("Ry")):
            flags["theta_y"] = True
        if flags:
            m.support(nid, **flags)

    for _, r in t["nodal_loads"].iterrows():
        nid = _i(r.get("Node"))
        if nid is None or nid not in node_ids:
            continue
        case = str(r.get("Case") or "default").strip() or "default"
        m.add_nodal_load(nid, case=case,
                         Fz=_f(r.get("Fz"), 0.0),
                         Mx=_f(r.get("Mx"), 0.0),
                         My=_f(r.get("My"), 0.0))

    for _, r in t["pressure_loads"].iterrows():
        eid = _i(r.get("Element"))
        if eid is None or eid not in elem_ids:
            continue
        p = _f(r.get("p"))
        if p is None:
            continue
        case = str(r.get("Case") or "default").strip() or "default"
        m.add_pressure(eid, p, case=case)

    return m


def init_state():
    if "tables" not in st.session_state:
        st.session_state.tables = blank_tables()
    st.session_state.setdefault("model", None)
    st.session_state.setdefault("model_error", None)
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("modal", None)
    st.session_state.setdefault("last_analysis", None)


def rebuild_model(show_toast=True):
    try:
        st.session_state.model = tables_to_model(st.session_state.tables)
        st.session_state.model_error = None
        if show_toast:
            st.toast("Modello ricostruito", icon="✅")
        return True
    except Exception as exc:
        st.session_state.model = None
        st.session_state.model_error = str(exc)
        return False


def _editor(name: str, label: str, **kwargs):
    df = st.session_state.tables[name]
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True,
                            key=f"editor_{name}", **kwargs)
    st.session_state.tables[name] = edited
    return edited


def tab_modello():
    st.subheader("Definizione del modello")

    def _n(name):
        return len(st.session_state.tables[name])

    with st.expander(f"Nodi ({_n('nodes')})", expanded=True):
        _editor("nodes", "Nodi")
    with st.expander(f"Materiali ({_n('materials')})"):
        _editor("materials", "Materiali")
    with st.expander(f"Sezioni ({_n('sections')})"):
        _editor("sections", "Sezioni")
    with st.expander(f"Elementi ({_n('elements')})"):
        _editor("elements", "Elementi")
    with st.expander(f"Vincoli ({_n('supports')})"):
        _editor("supports", "Vincoli")
    with st.expander(f"Carichi nodali ({_n('nodal_loads')})"):
        _editor("nodal_loads", "Carichi nodali")
    with st.expander(f"Pressioni ({_n('pressure_loads')})"):
        _editor("pressure_loads", "Pressioni")

    st.divider()
    if st.button("Applica modifiche", type="primary", use_container_width=True):
        rebuild_model()

    if st.session_state.model_error:
        st.error(f"Errore: {st.session_state.model_error}")
    elif st.session_state.model is not None:
        st.success(f"Modello: {len(st.session_state.model.nodes)} nodi, "
                   f"{len(st.session_state.model.elements)} elementi.")
        try:
            from platefeapy.plotting import plot_mesh
            fig = plot_mesh(st.session_state.model)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass


def tab_analisi():
    st.subheader("Esecuzione analisi")
    m = st.session_state.model
    if m is None:
        st.info("Nessun modello attivo.")
        return

    analysis = st.radio("Tipo di analisi",
                        ["Statica", "Modale"], horizontal=True)

    if analysis == "Statica":
        if st.button("Esegui analisi statica", type="primary"):
            try:
                res = m.solve()
                st.session_state.result = res
                st.session_state.last_analysis = "Statica"
                st.success("Analisi completata.")
            except Exception as exc:
                st.error(f"Errore: {exc}")
                st.code(traceback.format_exc())

    elif analysis == "Modale":
        n_modes = st.number_input("Numero modi", 1, 50, 6)
        if st.button("Esegui analisi modale", type="primary"):
            try:
                modal = m.modal(n_modes=int(n_modes))
                st.session_state.modal = modal
                st.session_state.last_analysis = "Modale"
                st.success("Analisi modale completata.")
            except Exception as exc:
                st.error(f"Errore: {exc}")
                st.code(traceback.format_exc())


def tab_risultati():
    st.subheader("Risultati")
    m = st.session_state.model
    last = st.session_state.last_analysis
    if m is None or last is None:
        st.info("Esegui prima un'analisi.")
        return

    if last == "Statica" and st.session_state.result is not None:
        res = st.session_state.result
        try:
            from platefeapy.plotting import (
                plot_contour, plot_deformed, plot_reactions, plot_supports,
            )
            what = st.radio(
                "Visualizza",
                ["Deformata", "Vincoli", "Reazioni", "Mx", "My", "Mxy", "Qx", "Qy", "w"],
                horizontal=True,
            )
            scale = st.number_input("Scala deformata", value=100.0)
            show_isolines = st.checkbox("Mostra iso-linee", value=True)
            if what == "Deformata":
                fig = plot_deformed(res, scale=scale)
            elif what == "Vincoli":
                fig = plot_supports(m)
            elif what == "Reazioni":
                fig = plot_reactions(res)
            else:
                fig = plot_contour(res, component=what, show_isolines=show_isolines)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            st.warning(f"Grafico non disponibile: {exc}")

        st.markdown("#### Spostamenti nodali")
        rows = []
        for nid in m.nodes:
            vals = res.displacements(nid)
            rows.append({"Node": nid, "w": vals[0],
                         "theta_x": vals[1], "theta_y": vals[2]})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

    elif last == "Modale" and st.session_state.modal is not None:
        modal = st.session_state.modal
        nmodes = len(modal.freq)
        mode = st.slider("Modo", 1, nmodes, 1) - 1
        try:
            from platefeapy.plotting import plot_mode
            fig = plot_mode(modal, i=mode, scale=100.0)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            st.warning(f"Grafico non disponibile: {exc}")

        df = pd.DataFrame({
            "Modo": np.arange(1, nmodes + 1),
            "Frequenza [Hz]": modal.freq,
            "Periodo [s]": modal.period,
        })
        st.dataframe(df, use_container_width=True)


def main():
    init_state()

    logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "Logo_PlatefeaPy.png")
    lc1, lc2, lc3 = st.columns([1, 1.4, 1])
    with lc2:
        if os.path.exists(logo):
            st.image(logo, use_container_width=True)

    st.markdown(
        "<p style='text-align:center;color:gray'>"
        "Definisci il modello nelle tabelle → esegui le analisi → visualizza i risultati.</p>",
        unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Modello", "Analisi", "Risultati"])
    with t1:
        tab_modello()
    with t2:
        tab_analisi()
    with t3:
        tab_risultati()


if __name__ == "__main__":
    main()
