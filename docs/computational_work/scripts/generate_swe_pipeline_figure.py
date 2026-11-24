"""
Generate an authentic 1980s/1990s Journal of Computational Physics / Edward Tufte
scientific monograph vector illustration of the Complete Simulation Lifecycle
(Entradas -> Loop Temporal t_k -> t_{k+1} + Forçantes -> Decisão t < T_final? ->
Produto Final Tensores m x n x K) in Casulli's Semi-Implicit Method for the 2D
Shallow Water Equations (2D SWE), following Casulli (1990).

Maintains the exact vintage 1980s/90s scientific engraving aesthetic (matching
Figure 1 and previous figures):
  - Warm archival paper canvas (#FCFBF7), classic booktabs double/single rules,
    sharp 90-degree drafting frames, and physical 2D/3D vector mini-illustrations.
  - Razor-sharp LaTeX Latin Modern Roman & Computer Modern Math typography.
  - Minimalist presenter layout: vector icons + short 2-4 word labels + math notation
    (zero explanatory paragraphs inside the blocks).

Visual Structure (Wide viewBox across the full simulation cycle):
  1. ENTRADAS (far left, feeding "Estado em t_k" via arrow "k = 0"):
     - Ícone 1 (Cenário fixo): isometric bathymetry basin h(x,y) cut by a deeper
       navigation channel + symbols: h(x,y), C_z, g, dx, dy, dt.
     - Ícone 2 (Quadro 0): calm flat water cross-section at rest: t_0: z^0 = u^0 = v^0 = 0.
  2. MIOLO DO LOOP TEMPORAL (t_k -> t_{k+1}):
     - Estado em t_k (3D water column icon z^k, u^k, v^k + H^k, gamma^k).
     - Etapa 1 — Advecção ELM (Pilar B, 0 Matrizes: curved backtracking N*tau + 4-node
       bilinear interpolation -> Fu^k, Fv^k).
     - FORÇANTES EM t_k (compact horizontal strip above Caminhos 1 & 2, feeding "entra em b"):
         * Sine wave icon: Maré M_2 (z_borda)
         * Wind streamlines icon: Vento (tau_x, tau_y)
         * Hatched wall icon: Margem (u_n = 0)
     - A Encruzilhada ("OU"):
         * Caminho 1 (Pilar A: 1 Matriz Pentadiagonal N x N -> Etapa 3 Velocidades with
           enlarged, crystal-clear explicit update equations).
         * Caminho 2 (Pilar C — ADI: 1º Meio-Passo m matrizes n x n + 2º Meio-Passo
           n matrizes m x m via Thomas O(N)).
     - Novo Estado t_{k+1} (3D water column icon z^{k+1}, u^{k+1}, v^{k+1}).
  3. DECISÃO & SAÍDA / PRODUTO FINAL (far right):
     - Diamond decision node "t < T_final?" exiting "Novo Estado t_{k+1}":
         * "Sim": connects to bottom dashed feedback loop (k <- k + 1).
         * "Não" (+ discrete "salvar quadro" icon): leads to "Produto Final — Tensores (m x n x K)".
     - Inside "Produto Final — Tensores (m x n x K)": 3 perspective stacked mini-graphics:
         * Stacked contour/gradient maps: z(x, y, t)
         * Stacked vector field grids: u(x, y, t), v(x, y, t)
         * 1D oscillatory tidal gauge time series: Marégrafo z(t)

Outputs:
  - ../figures/swe_casulli_pipeline.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_casulli_pipeline.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_casulli_pipeline.png (high-resolution raster preview)
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch
import matplotlib.patheffects as pe

# ---------------------------------------------------------------------------
# 1. Load Authentic LaTeX Latin Modern Roman Fonts & Computer Modern Math
# ---------------------------------------------------------------------------
miktex_lm_paths = glob.glob(
    r"C:\Program Files\MiKTeX_2\fonts\opentype\public\lm\lmroman*.otf"
)
for fp in miktex_lm_paths:
    fm.fontManager.addfont(fp)

plt.rcParams.update({
    "font.family": "Latin Modern Roman",
    "mathtext.fontset": "cm",
    "svg.fonttype": "path",       # Convert all glyphs to exact vector curves
    "pdf.fonttype": 42,           # Embed TrueType/OpenType outlines in PDF
    "axes.unicode_minus": True,
})

# ---------------------------------------------------------------------------
# 2. High-Contrast Typography & Edward Tufte Muted Cartographic Palette
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FCFBF7",       # Warm archival paper ivory
    "ink_primary": "#11161C",     # Deep, razor-sharp obsidian ink for titles & math
    "ink_secondary": "#222B35",   # Crisp dark charcoal for explanatory body text
    "ink_muted": "#687380",       # Clean slate gray for leader lines & drafting ticks
    "rule_dark": "#283648",       # Classic booktabs heavy rule
    "rule_light": "#C8BBAE",      # Subtle archival divider rule
    "water_front": "#A9CCE0",     # Front-left water column face (from Fig 1)
    "water_right": "#8EB8D1",     # Front-right water column face (from Fig 1)
    "water_top": "#D6EAF5",       # Top free-surface face
    "water_deep": "#5B92B5",      # Deep navigation channel water/bathymetry
    "water_edge": "#204B69",      # Crisp structural water edge
    "bed_front": "#C8BBAE",       # Geological cross-section left face (from Fig 1)
    "bed_right": "#B3A494",       # Geological cross-section right face (from Fig 1)
    "bed_top": "#E5DDD3",         # Shallow basin bed top
    "bed_channel": "#9E8D7B",     # Deep incised channel bed
    "bed_edge": "#5E4F41",        # Seabed contour & outline
    "z_node": "#145374",          # Deep cerulean for elevation z & main diagonal
    "u_node": "#8E321E",          # Deep Venetian terracotta for x-direction / Caminho 1
    "v_node": "#17575A",          # Deep sea-teal for y-direction / Caminho 2
    "amber_sub": "#9C5E14",       # Warm ochre/amber for ELM & temporal loop
    "mat_bg": "#FAF7F2",          # Matrix canvas background
    "cell_bg": "#F3EFEA",         # Subtle archival cell interior
    "cell_focus": "#E8F1F6",      # Highlighted interpolation cell
}


def crisp_text(ax, x, y, s, color="#11161C", stroke_w=0.16, bg_clear=False, pad=0.08, **kwargs):
    """
    Render razor-sharp LaTeX text by reinforcing ultra-thin Computer Modern
    hairlines with a micro self-colored stroke (no blurry halo!).
    When bg_clear=True, places a sharp rectangular paper mask behind text over lines.
    """
    if bg_clear:
        kwargs["bbox"] = dict(
            boxstyle=f"square,pad={pad}",
            facecolor=PALETTE["bg_canvas"],
            edgecolor="none",
            alpha=0.95,
        )
    t = ax.text(x, y, s, color=color, **kwargs)
    if stroke_w > 0:
        t.set_path_effects([pe.withStroke(linewidth=stroke_w, foreground=color)])
    return t


def draw_2d_arrow(
    ax, p0, p1, color, lw=1.35, mutation_scale=11.0, arrowstyle="-|>",
    zorder=20, ls="-", alpha=1.0, connectionstyle="arc3,rad=0.0"
):
    arr = FancyArrowPatch(
        p0, p1,
        arrowstyle=arrowstyle,
        mutation_scale=mutation_scale,
        color=color,
        linewidth=lw,
        linestyle=ls,
        alpha=alpha,
        connectionstyle=connectionstyle,
        shrinkA=0,
        shrinkB=0,
        zorder=zorder,
    )
    ax.add_patch(arr)
    return arr


def draw_drafting_frame(ax, x, y, w, h, ec="#4A5968", fc="none", lw=0.9, ls="-", double_top=False, zorder=4):
    """
    Draw a classic 1980s/90s sharp-cornered technical monograph frame
    (90-degree corners, optional double booktabs top rule).
    """
    ax.add_patch(Rectangle(
        (x, y), w, h,
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=zorder
    ))
    if double_top:
        ax.plot([x, x + w], [y + h - 0.06, y + h - 0.06],
                color=ec, lw=0.55, zorder=zorder + 1)


def draw_bathymetry_channel_icon(ax, cx, cy, w=1.75, h=1.05, zorder=10):
    """
    Draw an isometric 3D/2D bathymetry basin h(x,y) showing a shallow shelf
    cut longitudinally by a deeper navigation channel.
    """
    # Isometric parallelogram corners
    dx_iso = 0.35
    x0 = cx - 0.5 * w - 0.5 * dx_iso
    y0 = cy - 0.38 * h

    # Base geological block thickness
    dz_bed = 0.22

    # 4 outer corners of top basin surface
    P_bl = (x0, y0)
    P_br = (x0 + w, y0)
    P_tr = (x0 + w + dx_iso, y0 + h)
    P_tl = (x0 + dx_iso, y0 + h)

    # Shallow shelf top polygon
    ax.add_patch(Polygon(
        [P_bl, P_br, P_tr, P_tl], closed=True,
        facecolor=PALETTE["water_top"], edgecolor=PALETTE["water_edge"],
        lw=0.95, zorder=zorder + 1
    ))

    # Deeper central channel cutting diagonally across the basin
    c_l0, c_r0 = x0 + 0.34 * w, x0 + 0.66 * w
    c_l1, c_r1 = x0 + dx_iso + 0.38 * w, x0 + dx_iso + 0.70 * w
    # Outer bank contour of channel
    ax.add_patch(Polygon(
        [(x0 + 0.24 * w, y0), (x0 + 0.76 * w, y0),
         (x0 + dx_iso + 0.78 * w, y0 + h), (x0 + dx_iso + 0.26 * w, y0 + h)],
        closed=True, facecolor=PALETTE["water_front"], edgecolor="none", zorder=zorder + 2
    ))
    # Deep channel thalweg core
    ax.add_patch(Polygon(
        [(c_l0, y0), (c_r0, y0), (c_r1, y0 + h), (c_l1, y0 + h)],
        closed=True, facecolor=PALETTE["water_deep"], edgecolor=PALETTE["z_node"],
        lw=0.75, ls="--", zorder=zorder + 3
    ))

    # Front cross-section face showing the incised channel profile in the seabed!
    xs_prof = np.linspace(x0, x0 + w, 60)
    # Channel depression centered at x0 + 0.5*w
    xi_norm = (xs_prof - (x0 + 0.5 * w)) / (0.18 * w)
    ys_bed_top = y0 - 0.06 - 0.16 * np.exp(-(xi_norm ** 2))
    ys_bed_bot = np.full_like(xs_prof, y0 - dz_bed - 0.16)

    # Water cross-section in the front cut
    verts_wat_front = (
        [(x0, y0)]
        + list(zip(xs_prof, ys_bed_top))
        + [(x0 + w, y0)]
    )
    ax.add_patch(Polygon(
        verts_wat_front, closed=True,
        facecolor=PALETTE["water_right"], edgecolor=PALETTE["water_edge"],
        lw=0.85, zorder=zorder + 4
    ))

    # Geological seabed cross-section below the channel
    verts_bed_front = (
        list(zip(xs_prof, ys_bed_top))
        + [(x0 + w, y0 - dz_bed - 0.16), (x0, y0 - dz_bed - 0.16)]
    )
    ax.add_patch(Polygon(
        verts_bed_front, closed=True,
        facecolor=PALETTE["bed_front"], edgecolor=PALETTE["bed_edge"],
        lw=0.85, zorder=zorder + 3
    ))

    # Right geological side face
    ax.add_patch(Polygon(
        [(x0 + w, y0), (x0 + w + dx_iso, y0 + h),
         (x0 + w + dx_iso, y0 + h - dz_bed - 0.16), (x0 + w, y0 - dz_bed - 0.16)],
        closed=True, facecolor=PALETTE["bed_right"], edgecolor=PALETTE["bed_edge"],
        lw=0.85, zorder=zorder + 2
    ))

    # Tiny depth arrow h(x,y) inside the deep channel cut
    xc_ch = x0 + 0.5 * w
    draw_2d_arrow(ax, (xc_ch, y0), (xc_ch, y0 - 0.22),
                  color=PALETTE["ink_primary"], lw=0.9, mutation_scale=6.5,
                  arrowstyle="<|-|>", zorder=zorder + 6)


def draw_flat_rest_water_icon(ax, cx, cy, w=1.75, h=0.62, zorder=10):
    """
    Draw a miniature 2D cross-section of calm, flat water at rest (t_0: z^0 = u^0 = v^0 = 0).
    """
    x0 = cx - 0.5 * w
    y0 = cy - 0.5 * h
    h_bed = 0.24 * h
    h_wat = 0.54 * h

    # Seabed strip
    ax.add_patch(Rectangle(
        (x0, y0), w, h_bed,
        facecolor=PALETTE["bed_front"], edgecolor=PALETTE["bed_edge"],
        lw=0.85, zorder=zorder
    ))
    # Calm water body
    y_surf = y0 + h_bed + h_wat
    ax.add_patch(Rectangle(
        (x0, y0 + h_bed), w, h_wat,
        facecolor=PALETTE["water_top"], edgecolor="none", zorder=zorder + 1
    ))
    # Flat undisturbed surface line z = 0
    ax.plot([x0, x0 + w], [y_surf, y_surf],
            color=PALETTE["z_node"], lw=1.6, zorder=zorder + 3)
    ax.plot([x0 - 0.08, x0 + w + 0.08], [y_surf, y_surf],
            color=PALETTE["rule_dark"], lw=0.70, ls="--", zorder=zorder + 2)
    # Side walls
    ax.plot([x0, x0], [y0, y_surf + 0.10], color=PALETTE["bed_edge"], lw=0.95, zorder=zorder + 4)
    ax.plot([x0 + w, x0 + w], [y0, y_surf + 0.10], color=PALETTE["bed_edge"], lw=0.95, zorder=zorder + 4)


def draw_3d_water_column_icon(ax, ox, oy, scale=0.82, lbl_z=r"$z^k$", lbl_u=r"$u^k$", lbl_v=r"$v^k$", zorder=10):
    """
    Draw a miniature 3D axonometric water column with seabed bathymetry and
    staggered velocities (u, v, z) directly evoking Figure 1's art style.
    """
    ex = np.array([0.85, -0.22]) * scale
    ey = np.array([0.52, 0.28]) * scale
    ez = np.array([0.0, 1.0]) * scale

    def p3(x, y, z):
        pt = np.array([ox, oy]) + x * ex + y * ey + z * ez
        return pt[0], pt[1]

    zb0, zb1 = -0.85, -0.55
    zw_00, zw_10, zw_11, zw_01 = 0.52, 0.42, 0.50, 0.62

    # 1. Seabed front-left face
    bed_fl = [p3(0, 0, zb0), p3(1, 0, zb0), p3(1, 0, zb1), p3(0, 0, zb1)]
    ax.add_patch(Polygon(bed_fl, closed=True, facecolor=PALETTE["bed_front"],
                         edgecolor=PALETTE["bed_edge"], lw=0.85, zorder=zorder))

    # 2. Seabed front-right face
    bed_fr = [p3(1, 0, zb0), p3(1, 1, zb0), p3(1, 1, zb1), p3(1, 0, zb1)]
    ax.add_patch(Polygon(bed_fr, closed=True, facecolor=PALETTE["bed_right"],
                         edgecolor=PALETTE["bed_edge"], lw=0.85, zorder=zorder))

    # 3. Water front-left face
    wat_fl = [p3(0, 0, zb1), p3(1, 0, zb1), p3(1, 0, zw_10), p3(0, 0, zw_00)]
    ax.add_patch(Polygon(wat_fl, closed=True, facecolor=PALETTE["water_front"],
                         edgecolor=PALETTE["water_edge"], lw=1.0, zorder=zorder + 1))

    # 4. Water front-right face
    wat_fr = [p3(1, 0, zb1), p3(1, 1, zb1), p3(1, 1, zw_11), p3(1, 0, zw_10)]
    ax.add_patch(Polygon(wat_fr, closed=True, facecolor=PALETTE["water_right"],
                         edgecolor=PALETTE["water_edge"], lw=1.0, zorder=zorder + 1))

    # 5. Water top free-surface face
    wat_top = [p3(0, 0, zw_00), p3(1, 0, zw_10), p3(1, 1, zw_11), p3(0, 1, zw_01)]
    ax.add_patch(Polygon(wat_top, closed=True, facecolor=PALETTE["water_top"],
                         edgecolor=PALETTE["water_edge"], lw=1.1, zorder=zorder + 2))

    # Reference level z = 0 dashed contour
    p_d0, p_d1, p_d2 = p3(0, 0, 0.0), p3(1, 0, 0.0), p3(1, 1, 0.0)
    ax.plot([p_d0[0], p_d1[0], p_d2[0]], [p_d0[1], p_d1[1], p_d2[1]],
            color=PALETTE["rule_dark"], lw=0.70, ls="--", zorder=zorder + 3)

    # Center elevation node z on top surface
    pc_top = p3(0.5, 0.5, 0.51)
    ax.plot(*pc_top, marker="o", markersize=5.6, markerfacecolor=PALETTE["z_node"],
            markeredgecolor="white", markeredgewidth=0.8, zorder=zorder + 5)
    crisp_text(ax, pc_top[0] - 0.08, pc_top[1] + 0.20, lbl_z,
               color=PALETTE["z_node"], stroke_w=0.16, bg_clear=True, pad=0.03,
               fontsize=8.3, fontweight="bold", ha="center", va="bottom", zorder=zorder + 6)

    # Face velocity u on right vertical face
    pu_0 = p3(1.0, 0.5, -0.05)
    pu_1 = p3(1.46, 0.5, -0.05)
    draw_2d_arrow(ax, pu_0, pu_1, color=PALETTE["u_node"], lw=1.6, mutation_scale=9.0, zorder=zorder + 5)
    ax.plot(*pu_0, marker="s", markersize=4.2, markerfacecolor=PALETTE["u_node"],
            markeredgecolor="white", markeredgewidth=0.6, zorder=zorder + 6)
    crisp_text(ax, pu_1[0] + 0.04, pu_1[1] - 0.05, lbl_u,
               color=PALETTE["u_node"], stroke_w=0.15,
               fontsize=7.9, fontweight="bold", ha="left", va="center", zorder=zorder + 6)

    # Face velocity v on back-right horizontal face
    pv_0 = p3(0.5, 1.0, 0.10)
    pv_1 = p3(0.5, 1.52, 0.10)
    draw_2d_arrow(ax, pv_0, pv_1, color=PALETTE["v_node"], lw=1.6, mutation_scale=9.0, zorder=zorder + 5)
    ax.plot(*pv_0, marker="D", markersize=4.2, markerfacecolor=PALETTE["v_node"],
            markeredgecolor="white", markeredgewidth=0.6, zorder=zorder + 6)
    crisp_text(ax, pv_1[0] + 0.05, pv_1[1] + 0.03, lbl_v,
               color=PALETTE["v_node"], stroke_w=0.15, bg_clear=True, pad=0.03,
               fontsize=7.9, fontweight="bold", ha="left", va="bottom", zorder=zorder + 6)


def draw_mini_pentadiag(ax, x0, y0, size, zorder=12):
    """Draw a crisp 8x8 schematic Pentadiagonal matrix icon with vintage bracket frame."""
    n = 8
    bw = 3
    cs = size / n
    ax.add_patch(Rectangle(
        (x0, y0), size, size,
        facecolor=PALETTE["mat_bg"], edgecolor=PALETTE["ink_muted"],
        linewidth=0.75, zorder=zorder
    ))
    brk_w = 0.08
    for (bx, sgn) in [(x0 - 0.03, 1), (x0 + size + 0.03, -1)]:
        ax.plot([bx + sgn * brk_w, bx, bx, bx + sgn * brk_w],
                [y0, y0, y0 + size, y0 + size],
                color=PALETTE["ink_primary"], lw=1.2, zorder=zorder + 3)

    for r in range(n):
        for c in range(n):
            cx = x0 + c * cs
            cy = y0 + (n - 1 - r) * cs
            p = 0.07 * cs
            if r == c:
                col = PALETTE["z_node"]
            elif abs(r - c) == 1:
                col = PALETTE["u_node"]
            elif abs(r - c) == bw:
                col = PALETTE["v_node"]
            elif abs(r - c) < bw:
                col = "#F2CFC2"
            else:
                continue
            ax.add_patch(Rectangle(
                (cx + p, cy + p), cs - 2 * p, cs - 2 * p,
                facecolor=col, edgecolor="none", zorder=zorder + 2
            ))


def draw_mini_tridiag_stack(ax, x0, y0, size, off_col, count=4, zorder=12):
    """Draw a crisp stack of 4x4 schematic Tridiagonal matrices with sharp drafting borders."""
    n = 4
    cs = size / n
    dx_s, dy_s = 0.085, 0.075
    for s_idx in range(count - 1, -1, -1):
        xs = x0 + s_idx * dx_s
        ys = y0 + s_idx * dy_s
        zb = zorder + (count - s_idx) * 2
        ax.add_patch(Rectangle(
            (xs, ys), size, size,
            facecolor=PALETTE["mat_bg"] if s_idx == 0 else "#EFECE6",
            edgecolor=PALETTE["ink_primary"] if s_idx == 0 else PALETTE["ink_muted"],
            linewidth=1.0 if s_idx == 0 else 0.65,
            zorder=zb
        ))
        if s_idx == 0:
            for r in range(n):
                for c in range(n):
                    if abs(r - c) <= 1:
                        cx = xs + c * cs
                        cy = ys + (n - 1 - r) * cs
                        p = 0.08 * cs
                        col = PALETTE["z_node"] if r == c else off_col
                        ax.add_patch(Rectangle(
                            (cx + p, cy + p), cs - 2 * p, cs - 2 * p,
                            facecolor=col, edgecolor="none", zorder=zb + 1
                        ))


def draw_stacked_contour_maps_icon(ax, x0, y0, w=1.05, h=0.72, count=3, zorder=12):
    """
    Draw a perspective stack of 2D water elevation maps z(x, y, t) with blue
    gradient bands and level contours ("film frames" along time t).
    """
    dx_s, dy_s = 0.14, 0.11
    for s_idx in range(count - 1, -1, -1):
        xs = x0 + s_idx * dx_s
        ys = y0 + s_idx * dy_s
        zb = zorder + (count - s_idx) * 3
        ax.add_patch(Rectangle(
            (xs, ys), w, h,
            facecolor=PALETTE["water_top"] if s_idx == 0 else "#E2EEF5",
            edgecolor=PALETTE["water_edge"],
            linewidth=1.0 if s_idx == 0 else 0.70,
            zorder=zb
        ))
        if s_idx == 0:
            # Draw nested elliptical contour levels inside front frame
            th = np.linspace(0, 2 * np.pi, 60)
            cx_m, cy_m = xs + 0.52 * w, ys + 0.50 * h
            for (rx, ry, col_c) in [
                (0.38 * w, 0.34 * h, PALETTE["water_front"]),
                (0.24 * w, 0.21 * h, PALETTE["water_right"]),
                (0.11 * w, 0.10 * h, PALETTE["water_deep"]),
            ]:
                ax.fill(cx_m + rx * np.cos(th), cy_m + ry * np.sin(th),
                        color=col_c, edgecolor=PALETTE["z_node"], lw=0.55, zorder=zb + 1)


def draw_stacked_vector_grids_icon(ax, x0, y0, w=1.05, h=0.72, count=3, zorder=12):
    """
    Draw a perspective stack of 2D velocity field grids u(x,y,t), v(x,y,t)
    with grid hairlines and current vectors.
    """
    dx_s, dy_s = 0.14, 0.11
    for s_idx in range(count - 1, -1, -1):
        xs = x0 + s_idx * dx_s
        ys = y0 + s_idx * dy_s
        zb = zorder + (count - s_idx) * 3
        ax.add_patch(Rectangle(
            (xs, ys), w, h,
            facecolor=PALETTE["mat_bg"] if s_idx == 0 else "#EFECE6",
            edgecolor=PALETTE["v_node"],
            linewidth=1.0 if s_idx == 0 else 0.70,
            zorder=zb
        ))
        if s_idx == 0:
            # Internal 3x2 grid lines
            for gx in [xs + w / 3, xs + 2 * w / 3]:
                ax.plot([gx, gx], [ys, ys + h], color=PALETTE["rule_light"], lw=0.5, zorder=zb + 1)
            ax.plot([xs, xs + w], [ys + 0.5 * h, ys + 0.5 * h],
                    color=PALETTE["rule_light"], lw=0.5, zorder=zb + 1)
            # Current vector arrows inside grid
            for ix in range(3):
                for iy in range(2):
                    vx0 = xs + (ix + 0.25) * (w / 3)
                    vy0 = ys + (iy + 0.35) * (h / 2)
                    draw_2d_arrow(
                        ax, (vx0, vy0), (vx0 + 0.18, vy0 + 0.08 * (1 if iy == 0 else -0.5)),
                        color=PALETTE["u_node"] if (ix + iy) % 2 == 0 else PALETTE["v_node"],
                        lw=0.95, mutation_scale=6.0, zorder=zb + 2
                    )


def draw_tidal_gauge_series_icon(ax, x0, y0, w=1.25, h=0.65, zorder=12):
    """
    Draw a miniature 1D oscillatory time-series chart: Marégrafo z(t).
    """
    ax.add_patch(Rectangle(
        (x0, y0), w, h,
        facecolor="#FFFFFF", edgecolor=PALETTE["ink_muted"],
        linewidth=0.85, zorder=zorder
    ))
    # Zero equilibrium axis
    ym = y0 + 0.5 * h
    ax.plot([x0 + 0.06, x0 + w - 0.06], [ym, ym],
            color=PALETTE["rule_light"], lw=0.65, ls="--", zorder=zorder + 1)
    # Tidal harmonic curve z(t)
    ts = np.linspace(0, 1, 90)
    xs_t = x0 + 0.08 + ts * (w - 0.16)
    ys_t = ym + 0.32 * h * np.sin(2.5 * 2 * np.pi * ts) * (0.75 + 0.25 * np.cos(np.pi * ts))
    ax.plot(xs_t, ys_t, color=PALETTE["z_node"], lw=1.35, zorder=zorder + 2)


def build_figure():
    # Wide aspect ratio to accommodate Input -> Core Loop -> Decision -> Output cleanly
    fig, ax = plt.subplots(figsize=(19.2, 9.6), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    X_MIN, X_MAX = -11.45, 11.45

    # =======================================================================
    # TOP BOOKTABS HEADER (Classic 1980s/90s Monograph Double Rule)
    # =======================================================================
    ax.plot([X_MIN + 0.15, X_MAX - 0.15], [4.72, 4.72], color=PALETTE["rule_dark"], lw=1.35, zorder=15)
    ax.plot([X_MIN + 0.15, X_MAX - 0.15], [4.65, 4.65], color=PALETTE["rule_dark"], lw=0.55, zorder=15)

    crisp_text(
        ax, 0.0, 4.38,
        r"Ciclo Completo da Simulação e Fluxo de 1 Passo de Tempo ($t_k \rightarrow t_{k+1}$) no Método Semi-Implícito de Casulli ($N = m \cdot n$ células)",
        color=PALETTE["ink_primary"], stroke_w=0.20,
        fontsize=11.0, fontweight="bold", ha="center", va="center", zorder=28
    )
    crisp_text(
        ax, 0.0, 4.02,
        r"Princípio Geral: Sistemas lineares (matrizes) são resolvidos SOMENTE para a elevação $z$  —  Velocidades $u$ e $v$ são atualizadas por substituição direta ($0$ matrizes)",
        color=PALETTE["z_node"], stroke_w=0.16,
        fontsize=9.0, fontstyle="italic", ha="center", va="center", zorder=28
    )

    ax.plot([X_MIN + 0.15, X_MAX - 0.15], [3.78, 3.78], color=PALETTE["rule_dark"], lw=0.80, zorder=15)

    # Vertical dotted drafting dividers separating the macro stages
    for x_div in [-8.55, -6.15, -3.25, 4.75, 7.05]:
        ax.plot([x_div, x_div], [-3.40, 3.60], color=PALETTE["rule_light"], lw=0.75, ls=":", zorder=3)

    # =======================================================================
    # BLOCK 1 (FAR LEFT): ENTRADAS (Cenário Fixo + Quadro 0 -> seta "k = 0")
    # =======================================================================
    x_in, y_in, w_in, h_in = -11.25, -3.30, 2.45, 6.80
    draw_drafting_frame(ax, x_in, y_in, w_in, h_in,
                        ec=PALETTE["bed_edge"], fc="#F8F5F0", lw=1.10, double_top=True, zorder=5)

    cx_in = x_in + 0.5 * w_in
    crisp_text(
        ax, cx_in, 3.25,
        r"ENTRADAS",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=9.3, fontweight="bold", ha="center", va="top", zorder=20
    )
    ax.plot([x_in + 0.15, x_in + w_in - 0.15], [2.88, 2.88],
            color=PALETTE["rule_light"], lw=0.70, zorder=10)

    # Icon 1: Cenário fixo (isometric bathymetry basin h(x,y) cut by deeper channel)
    crisp_text(
        ax, cx_in, 2.68,
        r"1. Cenário Fixo",
        color=PALETTE["bed_edge"], stroke_w=0.17,
        fontsize=8.5, fontweight="bold", ha="center", va="top", zorder=20
    )
    draw_bathymetry_channel_icon(ax, cx=cx_in - 0.08, cy=1.55, w=1.60, h=0.88, zorder=12)

    crisp_text(
        ax, cx_in, 0.65,
        r"$h(x,y),\; C_z,\; g$" + "\n"
        + r"$\Delta x,\; \Delta y,\; \Delta t$",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=8.6, fontweight="bold", ha="center", va="top", linespacing=1.35, zorder=22
    )

    ax.plot([x_in + 0.15, x_in + w_in - 0.15], [-0.30, -0.30],
            color=PALETTE["rule_light"], lw=0.70, zorder=10)

    # Icon 2: Quadro 0 (calm flat water cross-section at rest)
    crisp_text(
        ax, cx_in, -0.52,
        r"2. Quadro $0$ (Repouso)",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.5, fontweight="bold", ha="center", va="top", zorder=20
    )
    draw_flat_rest_water_icon(ax, cx=cx_in, cy=-1.45, w=1.72, h=0.75, zorder=12)

    crisp_text(
        ax, cx_in, -2.22,
        r"$t_0:\; z^0 = u^0 = v^0 = 0$",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.6, fontweight="bold", ha="center", va="top", zorder=22
    )

    # Entry arrow from ENTRADAS into "Estado em t_k" labeled "k = 0"
    draw_2d_arrow(ax, (x_in + w_in + 0.02, 0.72), (-8.30, 0.72),
                  color=PALETTE["ink_primary"], lw=1.6, mutation_scale=11, zorder=25)
    crisp_text(
        ax, -8.55, 0.90,
        r"$k = 0$",
        color=PALETTE["ink_primary"], stroke_w=0.17, bg_clear=True, pad=0.04,
        fontsize=8.4, fontweight="bold", ha="center", va="bottom", zorder=26
    )

    # =======================================================================
    # COLUMN 0 (CORE START): ESTADO EM t_k
    # =======================================================================
    cx_s0 = -7.35
    crisp_text(
        ax, cx_s0, 3.25,
        r"ESTADO EM $t_k$",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=9.3, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, 2.95,
        r"Malha $m \times n$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.1, fontstyle="italic", ha="center", va="top", zorder=20
    )

    draw_3d_water_column_icon(
        ax, ox=cx_s0 - 0.56, oy=1.42, scale=0.82,
        lbl_z=r"$z_{i,j}^k$", lbl_u=r"$u_{i+1/2,j}^k$", lbl_v=r"$v_{i,j+1/2}^k$"
    )

    crisp_text(
        ax, cx_s0, 0.22,
        r"• Centro: $z_{i,j}^k$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, -0.10,
        r"• Faces L/O: $u_{i+1/2,j}^k$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, -0.42,
        r"• Faces N/S: $v_{i,j+1/2}^k$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )

    ax.plot([-8.30, -6.40], [-0.80, -0.80], color=PALETTE["rule_light"], lw=0.75, zorder=10)

    crisp_text(
        ax, cx_s0, -1.00,
        r"Coeficientes em $t_k$:",
        color=PALETTE["amber_sub"], stroke_w=0.17,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, -1.35,
        r"$H^k = h + z^k > 0$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=8.4, ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, -1.78,
        r"$\gamma^k = \dfrac{g\sqrt{(u^k)^2+(v^k)^2}}{C_z^2\, H^k}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=8.3, ha="center", va="top", zorder=20
    )

    # Arrow Estado em t_k -> Etapa 1 (ELM)
    draw_2d_arrow(ax, (-6.32, 0.72), (-5.98, 0.72),
                  color=PALETTE["ink_primary"], lw=1.6, mutation_scale=11, zorder=25)

    # =======================================================================
    # COLUMN 1: ETAPA 1 — ADVECÇÃO ELM (PILAR B)
    # =======================================================================
    cx_s1 = -4.70
    crisp_text(
        ax, cx_s1, 3.25,
        r"ETAPA 1 — ELM",
        color=PALETTE["amber_sub"], stroke_w=0.18,
        fontsize=9.3, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s1, 2.95,
        r"Pilar B ($0$ Matrizes)",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=8.1, fontstyle="italic", ha="center", va="top", zorder=20
    )

    # Classic 2x2 Grid Engraving for ELM Backtracking
    gx_e, gy_e, cs_e = cx_s1 - 0.88, 0.35, 0.88
    for ix in range(2):
        for iy in range(2):
            fc_e = PALETTE["cell_focus"] if (ix == 0 and iy == 0) else PALETTE["cell_bg"]
            ec_e = PALETTE["v_node"] if (ix == 0 and iy == 0) else PALETTE["ink_muted"]
            lw_e = 1.25 if (ix == 0 and iy == 0) else 0.70
            ax.add_patch(Rectangle(
                (gx_e + ix * cs_e, gy_e + iy * cs_e), cs_e, cs_e,
                facecolor=fc_e, edgecolor=ec_e, linewidth=lw_e,
                zorder=11 if (ix == 0 and iy == 0) else 8
            ))

    for (dx_c, dy_c) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        ax.plot(gx_e + dx_c * cs_e, gy_e + dy_c * cs_e,
                marker="D", markersize=4.6, markerfacecolor=PALETTE["v_node"],
                markeredgecolor="white", markeredgewidth=0.7, zorder=16)

    p_arr_elm = (gx_e + 2 * cs_e, gy_e + 2 * cs_e)
    p_foot_elm = (gx_e + 0.52 * cs_e, gy_e + 0.46 * cs_e)
    ax.plot(*p_arr_elm, marker="o", markersize=6.0, markerfacecolor=PALETTE["z_node"],
            markeredgecolor="white", markeredgewidth=0.8, zorder=18)
    ax.plot(*p_foot_elm, marker="*", markersize=8.5, markerfacecolor=PALETTE["u_node"],
            markeredgecolor="white", markeredgewidth=0.7, zorder=18)

    for (dx_c, dy_c) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        ax.plot([gx_e + dx_c * cs_e, p_foot_elm[0]],
                [gy_e + dy_c * cs_e, p_foot_elm[1]],
                color=PALETTE["v_node"], lw=0.70, ls="--", zorder=13)

    P0_e = np.array(p_arr_elm)
    P2_e = np.array(p_foot_elm)
    P1_e = np.array([gx_e + 0.95 * cs_e, gy_e + 1.55 * cs_e])
    s_e = np.linspace(0, 1, 60)
    curve_e = (
        ((1 - s_e) ** 2)[:, None] * P0_e
        + (2 * (1 - s_e) * s_e)[:, None] * P1_e
        + (s_e ** 2)[:, None] * P2_e
    )
    ax.plot(curve_e[:, 0], curve_e[:, 1], color=PALETTE["z_node"], lw=1.75, zorder=17)
    draw_2d_arrow(ax, tuple(curve_e[-4]), tuple(P2_e),
                  color=PALETTE["z_node"], lw=1.75, mutation_scale=10, zorder=17)

    for sv in [0.33, 0.66]:
        pt_s = (1 - sv) ** 2 * P0_e + 2 * (1 - sv) * sv * P1_e + (sv ** 2) * P2_e
        ax.plot(pt_s[0], pt_s[1], marker="o", markersize=4.3,
                markerfacecolor=PALETTE["amber_sub"], markeredgecolor="white",
                markeredgewidth=0.6, zorder=19)

    crisp_text(ax, gx_e + 2 * cs_e, gy_e + 2 * cs_e + 0.08, r"$(i, j)$ em $t_{k+1}$",
               color=PALETTE["z_node"], stroke_w=0.14,
               fontsize=7.7, fontweight="bold", ha="right", va="bottom", zorder=20)
    crisp_text(ax, gx_e + 1.05 * cs_e, gy_e + 1.15 * cs_e, r"$N\text{ passos }\tau$",
               color=PALETTE["amber_sub"], stroke_w=0.14, bg_clear=True, pad=0.03,
               fontsize=7.7, fontweight="bold", ha="left", va="center", zorder=20)
    crisp_text(ax, cx_s1, gy_e - 0.16, r"Pé $(i-a, j-b)$: 4 nós",
               color=PALETTE["v_node"], stroke_w=0.14,
               fontsize=7.8, fontweight="bold", ha="center", va="top", zorder=20)

    ax.plot([-5.85, -3.55], [-0.80, -0.80], color=PALETTE["rule_light"], lw=0.75, zorder=10)

    crisp_text(
        ax, cx_s1, -1.00,
        r"Termos advectados:",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=8.1, fontstyle="italic", ha="center", va="top", zorder=20
    )

    draw_drafting_frame(ax, cx_s1 - 0.90, -1.86, 1.80, 0.50,
                        ec=PALETTE["amber_sub"], fc=PALETTE["mat_bg"], lw=0.95, zorder=15)
    crisp_text(
        ax, cx_s1, -1.61,
        r"$F u_{i+1/2,j}^k,\; F v_{i,j+1/2}^k$",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=8.9, fontweight="bold", ha="center", va="center", zorder=22
    )
    crisp_text(
        ax, cx_s1, -2.02,
        r"(entram em $\mathbf{b}$)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.9, fontstyle="italic", ha="center", va="top", zorder=20
    )

    # =======================================================================
    # BLOCK 2 (TOP OF CENTER-RIGHT): FORÇANTES EM t_k (entra em b)
    # =======================================================================
    x_fc, y_fc, w_fc, h_fc = -2.65, 2.62, 7.10, 0.88
    draw_drafting_frame(ax, x_fc, y_fc, w_fc, h_fc,
                        ec=PALETTE["rule_dark"], fc="#FAF6EE", lw=0.95, zorder=8)

    crisp_text(
        ax, x_fc + 0.14, y_fc + 0.5 * h_fc,
        r"FORÇANTES" + "\n" + r"EM $t_k$:",
        color=PALETTE["ink_primary"], stroke_w=0.17,
        fontsize=8.1, fontweight="bold", ha="left", va="center", linespacing=1.15, zorder=20
    )

    # Mini-Icon 1: Onda senoidal — Maré M_2 (z_borda)
    x_m1 = -1.32
    ts_m = np.linspace(0, 2 * np.pi, 50)
    ax.plot(x_m1 + np.linspace(0, 0.60, 50), y_fc + 0.44 + 0.15 * np.sin(ts_m),
            color=PALETTE["z_node"], lw=1.45, zorder=15)
    ax.plot([x_m1, x_m1 + 0.60], [y_fc + 0.44, y_fc + 0.44],
            color=PALETTE["ink_muted"], lw=0.55, ls=":", zorder=14)
    crisp_text(
        ax, x_m1 + 0.68, y_fc + 0.5 * h_fc,
        r"Maré $M_2$ ($z_{\mathrm{borda}}$)",
        color=PALETTE["z_node"], stroke_w=0.15,
        fontsize=8.0, fontweight="bold", ha="left", va="center", zorder=20
    )

    # Vertical divider tick inside Forçantes bar
    ax.plot([0.68, 0.68], [y_fc + 0.14, y_fc + h_fc - 0.14], color=PALETTE["rule_light"], lw=0.70, zorder=10)

    # Mini-Icon 2: Linhas de vento com setas — Vento (\tau_x, \tau_y)
    x_m2 = 0.84
    for dy_w, dx_len in [(0.56, 0.52), (0.32, 0.42)]:
        draw_2d_arrow(ax, (x_m2, y_fc + dy_w), (x_m2 + dx_len, y_fc + dy_w),
                      color=PALETTE["v_node"], lw=1.2, mutation_scale=7.5, zorder=15)
    crisp_text(
        ax, x_m2 + 0.60, y_fc + 0.5 * h_fc,
        r"Vento ($\tau_x, \tau_y$)",
        color=PALETTE["v_node"], stroke_w=0.15,
        fontsize=8.0, fontweight="bold", ha="left", va="center", zorder=20
    )

    # Vertical divider tick inside Forçantes bar
    ax.plot([2.55, 2.55], [y_fc + 0.14, y_fc + h_fc - 0.14], color=PALETTE["rule_light"], lw=0.70, zorder=10)

    # Mini-Icon 3: Parede hachurada — Margem (u_n = 0)
    x_m3 = 2.72
    y_w0, y_w1 = y_fc + 0.18, y_fc + 0.70
    ax.plot([x_m3 + 0.24, x_m3 + 0.24], [y_w0, y_w1], color=PALETTE["bed_edge"], lw=1.5, zorder=15)
    for yh in np.linspace(y_w0, y_w1 - 0.10, 5):
        ax.plot([x_m3 + 0.24, x_m3 + 0.38], [yh, yh + 0.10], color=PALETTE["bed_edge"], lw=0.8, zorder=14)
    draw_2d_arrow(ax, (x_m3 - 0.04, y_fc + 0.44), (x_m3 + 0.21, y_fc + 0.44),
                  color=PALETTE["u_node"], lw=1.1, mutation_scale=6.5, zorder=15)
    crisp_text(
        ax, x_m3 + 0.45, y_fc + 0.5 * h_fc,
        r"Margem ($u_n = 0$)",
        color=PALETTE["bed_edge"], stroke_w=0.15,
        fontsize=8.0, fontweight="bold", ha="left", va="center", zorder=20
    )

    # Short vertical arrows descending from FORÇANTES into Caminho 1 AND via the OU junction to Caminho 2 ("entra em b")
    draw_2d_arrow(ax, (-0.85, y_fc), (-0.85, 2.16),
                  color=PALETTE["amber_sub"], lw=1.25, mutation_scale=8.5, zorder=22)
    # Branch from FORÇANTES down the left channel into the "OU" junction (feeding Caminho 1 OR Caminho 2!)
    ax.plot([-2.15, -2.15], [y_fc, 2.40], color=PALETTE["amber_sub"], lw=1.2, ls="--", zorder=20)
    ax.plot([-2.15, -3.05], [2.40, 2.40], color=PALETTE["amber_sub"], lw=1.2, ls="--", zorder=20)
    draw_2d_arrow(ax, (-3.05, 2.40), (-3.05, 1.18),
                  color=PALETTE["amber_sub"], lw=1.25, mutation_scale=8.5, ls="--", zorder=22)
    ax.plot(-3.05, 1.15, marker="o", markersize=4.2, color=PALETTE["amber_sub"], zorder=25)

    crisp_text(
        ax, -1.50, 2.38,
        r"entra em $\mathbf{b}$ (Caminho 1 ou 2)",
        color=PALETTE["amber_sub"], stroke_w=0.15, bg_clear=True, pad=0.03,
        fontsize=7.8, fontweight="bold", fontstyle="italic", ha="center", va="center", zorder=24
    )

    # =======================================================================
    # COLUMN 2 (CENTER-RIGHT): A ENCRUZILHADA (CAMINHO 1 OU CAMINHO 2)
    # =======================================================================
    x_fork, y_fork = -3.05, 0.35
    ax.plot([-3.48, x_fork], [y_fork, y_fork], color=PALETTE["ink_primary"], lw=1.4, zorder=18)
    ax.plot([x_fork, x_fork], [-1.65, 1.15], color=PALETTE["ink_primary"], lw=1.4, zorder=18)
    draw_2d_arrow(ax, (x_fork, 1.15), (-2.67, 1.15),
                  color=PALETTE["u_node"], lw=1.6, mutation_scale=10.5, zorder=22)
    draw_2d_arrow(ax, (x_fork, -1.65), (-2.67, -1.65),
                  color=PALETTE["v_node"], lw=1.6, mutation_scale=10.5, zorder=22)

    ax.add_patch(Rectangle(
        (x_fork - 0.23, 0.18), 0.46, 0.34,
        facecolor=PALETTE["bg_canvas"], edgecolor=PALETTE["ink_primary"],
        linewidth=1.1, zorder=26
    ))
    crisp_text(
        ax, x_fork, 0.35, "OU",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=8.2, fontweight="bold", ha="center", va="center", zorder=28
    )

    # -----------------------------------------------------------------------
    # UPPER BRANCH: CAMINHO 1 — ESQUEMA PENTADIAGONAL 2D (PILAR A PURO)
    # -----------------------------------------------------------------------
    x_b1, y_b1, w_b1, h_b1 = -2.65, -0.22, 7.10, 2.36
    draw_drafting_frame(ax, x_b1, y_b1, w_b1, h_b1,
                        ec=PALETTE["u_node"], fc="#FDF9F7", lw=1.15, double_top=True, zorder=5)

    crisp_text(
        ax, x_b1 + 0.16, y_b1 + h_b1 - 0.13,
        r"CAMINHO 1 — Esquema Pentadiagonal 2D (Pilar A Puro)",
        color=PALETTE["u_node"], stroke_w=0.18,
        fontsize=8.7, fontweight="bold", ha="left", va="top", zorder=22
    )

    # Step 2A: 1 Global Pentadiagonal Matrix
    draw_mini_pentadiag(ax, x0=-2.42, y0=0.05, size=1.26, zorder=15)

    crisp_text(
        ax, -1.02, 1.38,
        r"Etapa 2: Elevação $z^{k+1}$",
        color=PALETTE["u_node"], stroke_w=0.17,
        fontsize=8.3, fontweight="bold", ha="left", va="center", zorder=22
    )
    crisp_text(
        ax, -1.02, 1.02,
        r"1 Matriz $N \times N$ ($A\,\mathbf{z}^{k+1} = \mathbf{b}$)",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=7.9, fontweight="bold", ha="left", va="center", zorder=22
    )
    crisp_text(
        ax, -1.02, 0.45,
        r"• 5 diagonais (PCG / SOR)" + "\n"
        + r"• Calcula $z_{i,j}^{k+1}$ global",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.7, ha="left", va="center", linespacing=1.25, zorder=22
    )

    # Orthogonal arrow from Etapa 2 to Etapa 3 inside Upper Branch
    draw_2d_arrow(ax, (0.90, 0.85), (1.14, 0.85),
                  color=PALETTE["u_node"], lw=1.5, mutation_scale=10, zorder=22)

    # Step 3A: Widened frame [1.16, 4.34] with title strictly inside and crystal-clear + sign in denominator!
    draw_drafting_frame(ax, 1.16, -0.10, 3.18, 1.88,
                        ec=PALETTE["z_node"], fc="#FFFFFF", lw=0.95, zorder=14)
    crisp_text(
        ax, 2.75, 1.66,
        r"Etapa 3: Velocidades ($0$ Matrizes — Conta Direta)",
        color=PALETTE["z_node"], stroke_w=0.16,
        fontsize=7.4, fontweight="bold", ha="center", va="top", zorder=22
    )
    ax.plot([1.26, 4.24], [1.43, 1.43], color=PALETTE["rule_light"], lw=0.65, zorder=15)

    # Explicit velocity update equations with generous vertical space between fraction bar and (1 + dt*gamma^k)
    crisp_text(
        ax, 2.75, 1.04,
        r"$u^{k+1} = \dfrac{F u^k - g\Delta t\,\nabla_x z^{k+1} + \Delta t\,\tau_x}{1 + \Delta t\,\gamma^k}$",
        color=PALETTE["ink_primary"], stroke_w=0.17,
        fontsize=8.8, ha="center", va="center", zorder=24
    )
    crisp_text(
        ax, 2.75, 0.28,
        r"$v^{k+1} = \dfrac{F v^k - g\Delta t\,\nabla_y z^{k+1} + \Delta t\,\tau_y}{1 + \Delta t\,\gamma^k}$",
        color=PALETTE["ink_primary"], stroke_w=0.17,
        fontsize=8.8, ha="center", va="center", zorder=24
    )

    # -----------------------------------------------------------------------
    # LOWER BRANCH: CAMINHO 2 — VARIANTE ADI (PILAR C: SUBSTITUI O PILAR A)
    # -----------------------------------------------------------------------
    x_b2, y_b2, w_b2, h_b2 = -2.65, -3.30, 7.10, 2.82
    draw_drafting_frame(ax, x_b2, y_b2, w_b2, h_b2,
                        ec=PALETTE["v_node"], fc="#F7FBFA", lw=1.15, double_top=True, zorder=5)

    crisp_text(
        ax, x_b2 + 0.5 * w_b2, y_b2 + h_b2 - 0.14,
        r"CAMINHO 2 — Variante ADI (Pilar C, substitui o Pilar A): $m + n$ Tridiagonais via Thomas $\mathcal{O}(N)$",
        color=PALETTE["v_node"], stroke_w=0.18,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=22
    )

    # Half-Step 1 (Left inside Lower Branch): t_k -> t_{k+1/2} (Varredura x)
    draw_drafting_frame(ax, -2.50, -2.84, 3.22, 1.98,
                        ec=PALETTE["u_node"], fc="#FFFFFF", lw=0.90, zorder=14)
    crisp_text(
        ax, -0.89, -0.98,
        r"1º Meio-Passo ($t_k \rightarrow t_{k+1/2}$): Varredura $x$",
        color=PALETTE["u_node"], stroke_w=0.17,
        fontsize=8.1, fontweight="bold", ha="center", va="top", zorder=22
    )
    ax.plot([-2.40, 0.62], [-1.24, -1.24], color=PALETTE["rule_light"], lw=0.60, zorder=15)

    draw_mini_tridiag_stack(ax, x0=-2.36, y0=-2.30, size=0.80, off_col=PALETTE["u_node"], count=4, zorder=16)

    crisp_text(
        ax, -1.25, -1.56,
        r"$m$ Matrizes ($n \times n$)",
        color=PALETTE["u_node"], stroke_w=0.16,
        fontsize=8.0, fontweight="bold", ha="left", va="center", zorder=24
    )
    crisp_text(
        ax, -1.25, -1.98,
        r"• Thomas $\rightarrow z^{k+1/2}$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.8, ha="left", va="center", zorder=22
    )
    crisp_text(
        ax, -0.89, -2.62,
        r"Conta direta ($0$ matrizes): $\mathbf{u^{k+1/2}}$",
        color=PALETTE["z_node"], stroke_w=0.15,
        fontsize=7.7, fontweight="bold", ha="center", va="center", zorder=24
    )

    # Arrow from Half-Step 1 to Half-Step 2
    draw_2d_arrow(ax, (0.74, -1.85), (1.06, -1.85),
                  color=PALETTE["v_node"], lw=1.5, mutation_scale=9.5, zorder=22)

    # Half-Step 2 (Right inside Lower Branch): t_{k+1/2} -> t_{k+1} (Varredura y)
    draw_drafting_frame(ax, 1.08, -2.84, 3.22, 1.98,
                        ec=PALETTE["v_node"], fc="#FFFFFF", lw=0.90, zorder=14)
    crisp_text(
        ax, 2.69, -0.98,
        r"2º Meio-Passo ($t_{k+1/2} \rightarrow t_{k+1}$): Varredura $y$",
        color=PALETTE["v_node"], stroke_w=0.17,
        fontsize=8.1, fontweight="bold", ha="center", va="top", zorder=22
    )
    ax.plot([1.18, 4.20], [-1.24, -1.24], color=PALETTE["rule_light"], lw=0.60, zorder=15)

    draw_mini_tridiag_stack(ax, x0=1.22, y0=-2.30, size=0.80, off_col=PALETTE["v_node"], count=4, zorder=16)

    crisp_text(
        ax, 2.33, -1.56,
        r"$n$ Matrizes ($m \times m$)",
        color=PALETTE["v_node"], stroke_w=0.16,
        fontsize=8.0, fontweight="bold", ha="left", va="center", zorder=24
    )
    crisp_text(
        ax, 2.33, -1.98,
        r"• Thomas $\rightarrow z^{k+1}$ final",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.8, ha="left", va="center", zorder=22
    )
    crisp_text(
        ax, 2.69, -2.62,
        r"Conta direta ($0$ matrizes): $\mathbf{v^{k+1}}$",
        color=PALETTE["z_node"], stroke_w=0.15,
        fontsize=7.7, fontweight="bold", ha="center", va="center", zorder=24
    )

    crisp_text(
        ax, x_b2 + 0.5 * w_b2, -3.08,
        r"2ª varredura fecha o estado completo $(z^{k+1},\, u^{k+1},\, v^{k+1})$ em $t_{k+1}$",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=7.8, fontstyle="italic", ha="center", va="center", zorder=24
    )

    # =======================================================================
    # COLUMN 3: NOVO ESTADO EM t_{k+1}
    # =======================================================================
    x_join = 4.65
    ax.plot([x_b1 + w_b1, x_join], [1.15, 1.15], color=PALETTE["u_node"], lw=1.4, zorder=18)
    ax.plot([x_b2 + w_b2, x_join], [-1.65, -1.65], color=PALETTE["v_node"], lw=1.4, zorder=18)
    ax.plot([x_join, x_join], [-1.65, 1.15], color=PALETTE["z_node"], lw=1.4, zorder=18)
    draw_2d_arrow(ax, (x_join, 0.72), (4.95, 0.72),
                  color=PALETTE["z_node"], lw=1.6, mutation_scale=11, zorder=22)

    cx_s4 = 5.90
    crisp_text(
        ax, cx_s4, 3.25,
        r"NOVO ESTADO $t_{k+1}$",
        color=PALETTE["z_node"], stroke_w=0.18,
        fontsize=9.3, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s4, 2.95,
        r"$t_{k+1} = t_k + \Delta t$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.1, fontstyle="italic", ha="center", va="top", zorder=20
    )

    draw_3d_water_column_icon(
        ax, ox=cx_s4 - 0.56, oy=1.42, scale=0.82,
        lbl_z=r"$z_{i,j}^{k+1}$", lbl_u=r"$u_{i+1/2,j}^{k+1}$", lbl_v=r"$v_{i,j+1/2}^{k+1}$"
    )

    crisp_text(
        ax, cx_s4, 0.22,
        r"• Elevação $z_{i,j}^{k+1}$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s4, -0.12,
        r"• Velocidades $u^{k+1},\; v^{k+1}$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )

    ax.plot([5.00, 6.80], [-0.80, -0.80], color=PALETTE["rule_light"], lw=0.75, zorder=10)

    # Discrete "Salvar Quadro k+1" icon inside Novo Estado t_{k+1}
    draw_drafting_frame(ax, cx_s4 - 0.78, -1.92, 1.56, 0.72,
                        ec=PALETTE["z_node"], fc=PALETTE["mat_bg"], lw=0.85, zorder=14)
    crisp_text(
        ax, cx_s4, -1.40,
        r"Salva Quadro $k+1$",
        color=PALETTE["z_node"], stroke_w=0.16,
        fontsize=8.0, fontweight="bold", ha="center", va="center", zorder=20
    )
    crisp_text(
        ax, cx_s4, -1.72,
        r"$(z^{k+1},\, u^{k+1},\, v^{k+1})$",
        color=PALETTE["ink_primary"], stroke_w=0.14,
        fontsize=7.9, ha="center", va="center", zorder=20
    )

    # =======================================================================
    # BLOCK 3 (FAR RIGHT): DECISÃO "t < T_final?" & PRODUTO FINAL — TENSORES
    # =======================================================================
    # Decision Diamond "t_{k+1} < T_final?"
    cx_dec, cy_dec = 7.75, 0.72
    rx_d, ry_d = 0.66, 0.48

    draw_2d_arrow(ax, (6.82, cy_dec), (cx_dec - rx_d - 0.02, cy_dec),
                  color=PALETTE["z_node"], lw=1.6, mutation_scale=11, zorder=22)

    diamond_pts = [
        (cx_dec - rx_d, cy_dec),
        (cx_dec, cy_dec + ry_d),
        (cx_dec + rx_d, cy_dec),
        (cx_dec, cy_dec - ry_d),
    ]
    ax.add_patch(Polygon(
        diamond_pts, closed=True,
        facecolor=PALETTE["mat_bg"], edgecolor=PALETTE["ink_primary"],
        lw=1.15, zorder=24
    ))
    crisp_text(
        ax, cx_dec, cy_dec,
        r"$t_{k+1} < T_{\mathrm{final}}$?",
        color=PALETTE["ink_primary"], stroke_w=0.17,
        fontsize=7.9, fontweight="bold", ha="center", va="center", zorder=26
    )

    # Branch "Sim" (downward from diamond to the bottom dashed feedback loop k <- k + 1)
    y_loop = -3.85
    ax.plot([cx_dec, cx_dec], [cy_dec - ry_d, y_loop],
            color=PALETTE["amber_sub"], lw=1.5, ls="--", zorder=18)
    ax.plot([cx_dec, cx_s0], [y_loop, y_loop],
            color=PALETTE["amber_sub"], lw=1.5, ls="--", zorder=18)
    draw_2d_arrow(ax, (cx_s0, y_loop), (cx_s0, -2.55),
                  color=PALETTE["amber_sub"], lw=1.6, mutation_scale=11, zorder=22)

    crisp_text(
        ax, cx_dec + 0.12, cy_dec - ry_d - 0.25,
        "Sim",
        color=PALETTE["amber_sub"], stroke_w=0.17,
        fontsize=8.3, fontweight="bold", ha="left", va="center", zorder=26
    )

    crisp_text(
        ax, -0.20, y_loop,
        r"Loop Temporal ($k \leftarrow k + 1$): Atualiza coeficientes $H^k = h + z^k$ e $\gamma^k$ (esparsidade fixa)",
        color=PALETTE["amber_sub"], stroke_w=0.17, bg_clear=True, pad=0.12,
        fontsize=8.6, fontweight="bold", ha="center", va="center", zorder=26
    )

    # Branch "Não" (rightward from diamond into "Produto Final — Tensores (m x n x K)")
    x_out, y_out, w_out, h_out = 8.85, -3.30, 2.40, 6.80
    draw_2d_arrow(ax, (cx_dec + rx_d, cy_dec), (x_out - 0.02, cy_dec),
                  color=PALETTE["z_node"], lw=1.6, mutation_scale=11, zorder=22)
    crisp_text(
        ax, 0.5 * (cx_dec + rx_d + x_out), cy_dec + 0.14,
        "Não",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.3, fontweight="bold", ha="center", va="bottom", zorder=26
    )

    # Output Block Frame: PRODUTO FINAL — TENSORES (m x n x K)
    draw_drafting_frame(ax, x_out, y_out, w_out, h_out,
                        ec=PALETTE["z_node"], fc="#F5F9FC", lw=1.15, double_top=True, zorder=5)

    cx_out = x_out + 0.5 * w_out
    crisp_text(
        ax, cx_out, 3.25,
        r"PRODUTO FINAL",
        color=PALETTE["z_node"], stroke_w=0.18,
        fontsize=9.3, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_out, 2.95,
        r"Tensores ($m \times n \times K$)",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=20
    )
    ax.plot([x_out + 0.15, x_out + w_out - 0.15], [2.62, 2.62],
            color=PALETTE["rule_light"], lw=0.70, zorder=10)

    # Stacked Graphic 1: Pilha de mapas em degradê azul/curvas de nível z(x, y, t)
    draw_stacked_contour_maps_icon(ax, x0=cx_out - 0.65, y0=1.35, w=1.02, h=0.72, count=3, zorder=14)
    crisp_text(
        ax, cx_out, 1.15,
        r"Elevação $z(x, y, t)$",
        color=PALETTE["z_node"], stroke_w=0.16,
        fontsize=8.2, fontweight="bold", ha="center", va="top", zorder=22
    )

    ax.plot([x_out + 0.18, x_out + w_out - 0.18], [0.70, 0.70],
            color=PALETTE["rule_light"], lw=0.65, ls=":", zorder=10)

    # Stacked Graphic 2: Pilha de grades com vetores/setas de corrente u(x, y, t), v(x, y, t)
    draw_stacked_vector_grids_icon(ax, x0=cx_out - 0.65, y0=-0.55, w=1.02, h=0.72, count=3, zorder=14)
    crisp_text(
        ax, cx_out, -0.75,
        r"Correntes $u(x,y,t),\; v(x,y,t)$",
        color=PALETTE["v_node"], stroke_w=0.16,
        fontsize=8.1, fontweight="bold", ha="center", va="top", zorder=22
    )

    ax.plot([x_out + 0.18, x_out + w_out - 0.18], [-1.20, -1.20],
            color=PALETTE["rule_light"], lw=0.65, ls=":", zorder=10)

    # Stacked Graphic 3: Mini gráfico 1D de série temporal oscilatória — Marégrafo z(t)
    draw_tidal_gauge_series_icon(ax, x0=cx_out - 0.72, y0=-2.35, w=1.44, h=0.78, zorder=14)
    crisp_text(
        ax, cx_out, -2.55,
        r"Marégrafo $z(t)$",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=8.2, fontweight="bold", ha="center", va="top", zorder=22
    )

    # Classic bottom double rule closing the figure cleanly below the temporal loop
    ax.plot([X_MIN + 0.15, X_MAX - 0.15], [-4.30, -4.30], color=PALETTE["rule_dark"], lw=0.55, zorder=15)
    ax.plot([X_MIN + 0.15, X_MAX - 0.15], [-4.37, -4.37], color=PALETTE["rule_dark"], lw=1.35, zorder=15)

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(-4.55, 4.90)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.12)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_casulli_pipeline.svg"
    pdf_path = out_dir / "swe_casulli_pipeline.pdf"
    png_path = out_dir / "swe_casulli_pipeline.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
