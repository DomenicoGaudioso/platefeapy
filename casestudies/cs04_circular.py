"""Caso studio CS04: piastra circolare meshata con Gmsh.

Riferimento classico: Timoshenko & Woinowsky-Krieger, "Theory of Plates and
Shells", formule per piastra circolare soggetta a pressione uniforme.

La mesh e' generata con Gmsh come dominio circolare nativo a quadrilateri:
un nucleo centrale e quattro patch anulari ricombinate. Il bordo esterno e'
un cerchio discretizzato da archi Gmsh, non un rettangolo ritagliato.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from platefeapy import Material, Model, ShellSection
from platefeapy.plotting import (
    plot_contour, plot_deformed, plot_mesh, plot_reactions, plot_supports,
)

try:
    from .common import (
        D_bending,
        header,
        print_check,
        save_figure,
        timoshenko_circular_clamped_wmax,
        timoshenko_circular_ss_wmax,
    )
except ImportError:  # pragma: no cover - standalone execution
    from common import (
        D_bending,
        header,
        print_check,
        save_figure,
        timoshenko_circular_clamped_wmax,
        timoshenko_circular_ss_wmax,
    )


def _import_gmsh():
    try:
        import gmsh  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise ImportError(
            "CS04 richiede Gmsh: installare `pip install gmsh` oppure "
            "`pip install -e .[mesh]`."
        ) from exc
    return gmsh


def _generate_gmsh_disk_quads(R: float, n_el: int) -> tuple[list[tuple[float, float]], list[list[int]]]:
    """Genera una mesh Q4 circolare con Gmsh e restituisce nodi e quadrilateri."""
    gmsh = _import_gmsh()
    already_initialized = bool(getattr(gmsh, "isInitialized", lambda: 0)())
    if not already_initialized:
        gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.clear()
        gmsh.model.add("platefeapy_circular_plate")

        n_outer = max(16, int(n_el))
        n_radial = max(4, int(round(n_el / 4)))
        a = 0.22 * R

        inner_pts = [
            gmsh.model.geo.addPoint(-a, -a, 0.0),
            gmsh.model.geo.addPoint(a, -a, 0.0),
            gmsh.model.geo.addPoint(a, a, 0.0),
            gmsh.model.geo.addPoint(-a, a, 0.0),
        ]
        outer_pts = [
            gmsh.model.geo.addPoint(0.0, -R, 0.0),
            gmsh.model.geo.addPoint(R, 0.0, 0.0),
            gmsh.model.geo.addPoint(0.0, R, 0.0),
            gmsh.model.geo.addPoint(-R, 0.0, 0.0),
        ]
        center = gmsh.model.geo.addPoint(0.0, 0.0, 0.0)

        inner_lines = []
        for i in range(4):
            line = gmsh.model.geo.addLine(inner_pts[i], inner_pts[(i + 1) % 4])
            gmsh.model.geo.mesh.setTransfiniteCurve(line, n_outer + 1)
            inner_lines.append(line)

        center_loop = gmsh.model.geo.addCurveLoop(inner_lines)
        center_surface = gmsh.model.geo.addPlaneSurface([center_loop])
        gmsh.model.geo.mesh.setTransfiniteSurface(center_surface)
        gmsh.model.geo.mesh.setRecombine(2, center_surface)

        for i in range(4):
            conn_a = gmsh.model.geo.addLine(inner_pts[i], outer_pts[i])
            arc = gmsh.model.geo.addCircleArc(outer_pts[i], center, outer_pts[(i + 1) % 4])
            conn_b = gmsh.model.geo.addLine(inner_pts[(i + 1) % 4], outer_pts[(i + 1) % 4])
            gmsh.model.geo.mesh.setTransfiniteCurve(conn_a, n_radial + 1)
            gmsh.model.geo.mesh.setTransfiniteCurve(conn_b, n_radial + 1)
            gmsh.model.geo.mesh.setTransfiniteCurve(arc, n_outer + 1)
            loop = gmsh.model.geo.addCurveLoop([inner_lines[i], conn_b, -arc, -conn_a])
            surface = gmsh.model.geo.addPlaneSurface([loop])
            gmsh.model.geo.mesh.setTransfiniteSurface(surface)
            gmsh.model.geo.mesh.setRecombine(2, surface)

        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(2)

        node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
        coord_by_tag = {
            int(tag): (float(node_coords[3 * i]), float(node_coords[3 * i + 1]))
            for i, tag in enumerate(node_tags)
        }

        quad_tags: list[list[int]] = []
        element_types, _, element_node_tags = gmsh.model.mesh.getElements(2)
        for gmsh_type, flat_nodes in zip(element_types, element_node_tags):
            if int(gmsh_type) != 3:
                continue
            vals = [int(v) for v in flat_nodes]
            for k in range(0, len(vals), 4):
                quad_tags.append(vals[k:k + 4])
        if not quad_tags:
            raise RuntimeError("Gmsh non ha generato quadrilateri Q4 per CS04.")

        used_tags = sorted({tag for quad in quad_tags for tag in quad})
        tag_to_id = {tag: idx + 1 for idx, tag in enumerate(used_tags)}
        nodes = [coord_by_tag[tag] for tag in used_tags]
        quads = [[tag_to_id[tag] for tag in quad] for quad in quad_tags]
        return nodes, quads
    finally:
        if not already_initialized:
            gmsh.finalize()


def build_circular_plate(R: float, n_el: int, bc: str, theory: str = "mindlin"):
    """Costruisce una piastra circolare Q4 mappata direttamente sul disco.

    bc: 'ss' oppure 'clamped'
    """
    if n_el < 8:
        raise ValueError("n_el deve essere almeno 8")

    m = Model()
    nodes, quads = _generate_gmsh_disk_quads(R, n_el)
    for nid, (x, y) in enumerate(nodes, start=1):
        m.add_node(nid, x, y)

    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)

    for eid, quad in enumerate(quads, start=1):
        m.add_plate(eid, quad, mat, sec, theory=theory)

    boundary_ids = {
        nid for nid, node in m.nodes.items()
        if abs((node.x ** 2 + node.y ** 2) ** 0.5 - R) <= max(1e-8, 1e-6 * R)
    }
    for node_id in boundary_ids:
        if bc == "ss":
            m.fix(node_id, ["w"])
        elif bc == "clamped":
            m.fix(node_id)
        else:
            raise ValueError("bc deve essere 'ss' oppure 'clamped'")

    return m, list(m.elements), list(m.nodes), sorted(boundary_ids)


def main() -> None:
    R = 1.0
    p = -1000.0
    E, nu, t = 210e9, 0.3, 0.01
    D = D_bending(E, nu, t)

    header("CS04 - Piastra circolare meshata con Gmsh")
    print(f"  R = {R} m, t = {t} m, p = {p} Pa, E = {E:.2e} Pa, nu = {nu}")
    print(f"  D = {D:.4e} N m")
    print("  Mesh: Gmsh Q4 circolare nativa, senza rettangolo esterno")
    print()

    for bc_label, bc in [("SS (w=0)", "ss"), ("Incastrata (w=0, dw/dr=0)", "clamped")]:
        if bc == "ss":
            w_ex = timoshenko_circular_ss_wmax(p, R, E, nu, t)
        else:
            w_ex = timoshenko_circular_clamped_wmax(p, R, E, nu, t)
        print(f"  -- {bc_label} --")
        print(f"  w_max esatto = {w_ex:.6e} m")
        print(f"  {'mesh':>10s}  {'w_max FEM':>12s}  {'err %':>8s}")
        print("  " + "-" * 40)
        for n_el in (12, 18, 24, 32):
            m, elems, node_ids, _ = build_circular_plate(R, n_el, bc=bc)
            for eid in elems:
                m.add_pressure(eid, p)
            res = m.solve()
            w_fem = max(abs(res.displacement(nid, "w")) for nid in node_ids)
            err = abs(w_fem - w_ex) / w_ex * 100
            print(f"  {n_el:>4d}x{n_el:<4d}  {w_fem:12.4e}  {err:7.3f}%")
        print()

    bc = "ss"
    n_el = 32
    m, elems, node_ids, _ = build_circular_plate(R, n_el, bc=bc)
    for eid in elems:
        m.add_pressure(eid, p)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs04_mesh_{bc}_{n_el}.png")
    save_figure(plot_supports(m), f"cs04_supports_{bc}_{n_el}.png",
                title="Vincoli piastra circolare SS")
    save_figure(plot_deformed(res, scale=400), f"cs04_deformed_{bc}_{n_el}.png",
                title="Deformata circolare SS (scala 400x)")
    save_figure(plot_contour(res, "w"), f"cs04_w_map_{bc}_{n_el}.png",
                title="Spostamento w [m] (vista piana)")
    save_figure(plot_contour(res, "Mx"), f"cs04_Mx_{bc}_{n_el}.png",
                title="Mx [N m/m]")
    save_figure(plot_contour(res, "My"), f"cs04_My_{bc}_{n_el}.png",
                title="My [N m/m]")
    save_figure(plot_reactions(res), f"cs04_reactions_{bc}_{n_el}.png",
                title="Reazioni vincolari piastra circolare SS")

    w_fem = max(abs(res.displacement(nid, "w")) for nid in node_ids)
    w_ex = timoshenko_circular_ss_wmax(p, R, E, nu, t)
    print_check("w_max al centro (SS)", w_fem, w_ex, tol=0.10)
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
