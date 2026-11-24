"""
Generate an authentic 1980s/1990s Journal of Computational Physics / Edward Tufte
scientific monograph vector illustration of the Complete Algorithmic Pipeline for
1 Time Step (t_k -> t_{k+1}) in Casulli's Semi-Implicit Method for the 2D Shallow
Water Equations (2D SWE), following Casulli (1990).

Vintage 1980s/90s scientific engraving aesthetic (matching Figure 1):
  - NO rounded UI boxes, NO pill badges, NO colored "app cards".
  - Open archival paper canvas (#FCFBF7) structured with classic LaTeX booktabs
    double/single horizontal rules, sharp 90-degree drafting hairlines, and
    physical 2D/3D staggered grid & matrix diagrams floating directly on the paper.
  - Razor-sharp LaTeX Latin Modern Roman & Computer Modern Math typography.
  - Full-sized, legible explicit velocity update equations showing linearized
    bottom friction (1 + dt*gamma^k) and wind stress (tau_x, tau_y).
  - Clear notation in the ADI branch explaining how the full velocity state
    (u^{k+1}, v^{k+1}) is completed at t_{k+1}.

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
#    (Identical to Figure 1)
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
    "water_edge": "#204B69",      # Crisp structural water edge
    "bed_front": "#C8BBAE",       # Geological cross-section left face (from Fig 1)
    "bed_right": "#B3A494",       # Geological cross-section right face (from Fig 1)
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
    ax, p0, p1, color, lw=1.35, mutation_scale=11.5, arrowstyle="-|>",
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


def draw_3d_water_column_icon(ax, ox, oy, scale=1.0, lbl_z=r"$z^k$", lbl_u=r"$u^k$", lbl_v=r"$v^k$", zorder=10):
    """
    Draw a miniature 3D axonometric water column with seabed bathymetry and
    staggered velocities (u, v, z) directly evoking Figure 1's art style!
    """
    ex = np.array([0.85, -0.22]) * scale
    ey = np.array([0.52, 0.28]) * scale
    ez = np.array([0.0, 1.0]) * scale

    def p3(x, y, z):
        pt = np.array([ox, oy]) + x * ex + y * ey + z * ez
        return pt[0], pt[1]

    # Seabed base block: z from -0.85 to -0.55
    zb0, zb1 = -0.85, -0.55
    # Water column: z from -0.55 to +0.55 (with gentle wave tilt on top)
    zw_00, zw_10, zw_11, zw_01 = 0.52, 0.42, 0.50, 0.62

    # 1. Seabed front-left face (y = 0, x in [0, 1])
    bed_fl = [p3(0, 0, zb0), p3(1, 0, zb0), p3(1, 0, zb1), p3(0, 0, zb1)]
    ax.add_patch(Polygon(bed_fl, closed=True, facecolor=PALETTE["bed_front"],
                         edgecolor=PALETTE["bed_edge"], lw=0.9, zorder=zorder))

    # 2. Seabed front-right face (x = 1, y in [0, 1])
    bed_fr = [p3(1, 0, zb0), p3(1, 1, zb0), p3(1, 1, zb1), p3(1, 0, zb1)]
    ax.add_patch(Polygon(bed_fr, closed=True, facecolor=PALETTE["bed_right"],
                         edgecolor=PALETTE["bed_edge"], lw=0.9, zorder=zorder))

    # 3. Water front-left face (y = 0, x in [0, 1])
    wat_fl = [p3(0, 0, zb1), p3(1, 0, zb1), p3(1, 0, zw_10), p3(0, 0, zw_00)]
    ax.add_patch(Polygon(wat_fl, closed=True, facecolor=PALETTE["water_front"],
                         edgecolor=PALETTE["water_edge"], lw=1.05, zorder=zorder + 1))

    # 4. Water front-right face (x = 1, y in [0, 1])
    wat_fr = [p3(1, 0, zb1), p3(1, 1, zb1), p3(1, 1, zw_11), p3(1, 0, zw_10)]
    ax.add_patch(Polygon(wat_fr, closed=True, facecolor=PALETTE["water_right"],
                         edgecolor=PALETTE["water_edge"], lw=1.05, zorder=zorder + 1))

    # 5. Water top free-surface face (z = zw)
    wat_top = [p3(0, 0, zw_00), p3(1, 0, zw_10), p3(1, 1, zw_11), p3(0, 1, zw_01)]
    ax.add_patch(Polygon(wat_top, closed=True, facecolor=PALETTE["water_top"],
                         edgecolor=PALETTE["water_edge"], lw=1.15, zorder=zorder + 2))

    # Reference level z = 0 dashed contour on front faces
    p_d0, p_d1, p_d2 = p3(0, 0, 0.0), p3(1, 0, 0.0), p3(1, 1, 0.0)
    ax.plot([p_d0[0], p_d1[0], p_d2[0]], [p_d0[1], p_d1[1], p_d2[1]],
            color=PALETTE["rule_dark"], lw=0.75, ls="--", zorder=zorder + 3)

    # Center elevation node z on top surface
    pc_top = p3(0.5, 0.5, 0.51)
    ax.plot(*pc_top, marker="o", markersize=6.0, markerfacecolor=PALETTE["z_node"],
            markeredgecolor="white", markeredgewidth=0.9, zorder=zorder + 5)
    crisp_text(ax, pc_top[0] - 0.10, pc_top[1] + 0.22, lbl_z,
               color=PALETTE["z_node"], stroke_w=0.17, bg_clear=True, pad=0.04,
               fontsize=8.6, fontweight="bold", ha="center", va="bottom", zorder=zorder + 6)

    # Face velocity u on right vertical face (x = 1, y = 0.5)
    pu_0 = p3(1.0, 0.5, -0.05)
    pu_1 = p3(1.48, 0.5, -0.05)
    draw_2d_arrow(ax, pu_0, pu_1, color=PALETTE["u_node"], lw=1.7, mutation_scale=9.5, zorder=zorder + 5)
    ax.plot(*pu_0, marker="s", markersize=4.5, markerfacecolor=PALETTE["u_node"],
            markeredgecolor="white", markeredgewidth=0.7, zorder=zorder + 6)
    crisp_text(ax, pu_1[0] + 0.04, pu_1[1] - 0.06, lbl_u,
               color=PALETTE["u_node"], stroke_w=0.16,
               fontsize=8.2, fontweight="bold", ha="left", va="center", zorder=zorder + 6)

    # Face velocity v on back-right horizontal face (x = 0.5, y = 1.0)
    pv_0 = p3(0.5, 1.0, 0.10)
    pv_1 = p3(0.5, 1.55, 0.10)
    draw_2d_arrow(ax, pv_0, pv_1, color=PALETTE["v_node"], lw=1.7, mutation_scale=9.5, zorder=zorder + 5)
    ax.plot(*pv_0, marker="D", markersize=4.5, markerfacecolor=PALETTE["v_node"],
            markeredgecolor="white", markeredgewidth=0.7, zorder=zorder + 6)
    crisp_text(ax, pv_1[0] + 0.06, pv_1[1] + 0.04, lbl_v,
               color=PALETTE["v_node"], stroke_w=0.16, bg_clear=True, pad=0.04,
               fontsize=8.2, fontweight="bold", ha="left", va="bottom", zorder=zorder + 6)


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
    # Classic square matrix brackets [ ]
    brk_w = 0.09
    for (bx, sgn) in [(x0 - 0.03, 1), (x0 + size + 0.03, -1)]:
        ax.plot([bx + sgn * brk_w, bx, bx, bx + sgn * brk_w],
                [y0, y0, y0 + size, y0 + size],
                color=PALETTE["ink_primary"], lw=1.25, zorder=zorder + 3)

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
    dx_s, dy_s = 0.09, 0.08
    for s_idx in range(count - 1, -1, -1):
        xs = x0 + s_idx * dx_s
        ys = y0 + s_idx * dy_s
        zb = zorder + (count - s_idx) * 2
        ax.add_patch(Rectangle(
            (xs, ys), size, size,
            facecolor=PALETTE["mat_bg"] if s_idx == 0 else "#EFECE6",
            edgecolor=PALETTE["ink_primary"] if s_idx == 0 else PALETTE["ink_muted"],
            linewidth=1.05 if s_idx == 0 else 0.70,
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


def build_figure():
    fig, ax = plt.subplots(figsize=(16.2, 9.3), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # =======================================================================
    # TOP BOOKTABS HEADER (Classic 1980s/90s Monograph Double Rule)
    # =======================================================================
    ax.plot([-8.45, 8.45], [4.52, 4.52], color=PALETTE["rule_dark"], lw=1.35, zorder=15)
    ax.plot([-8.45, 8.45], [4.45, 4.45], color=PALETTE["rule_dark"], lw=0.55, zorder=15)

    crisp_text(
        ax, 0.0, 4.18,
        r"Fluxo Algorítmico de 1 Passo de Tempo ($t_k \rightarrow t_{k+1} = t_k + \Delta t$) na Malha Escalonada ($N = m \cdot n$ células)",
        color=PALETTE["ink_primary"], stroke_w=0.20,
        fontsize=11.0, fontweight="bold", ha="center", va="center", zorder=28
    )
    crisp_text(
        ax, 0.0, 3.82,
        r"Regra de Ouro de Casulli: Sistemas lineares (matrizes) são resolvidos SOMENTE para a elevação $z$  —  Velocidades $u$ e $v$ são atualizadas por substituição direta ($0$ matrizes)",
        color=PALETTE["z_node"], stroke_w=0.16,
        fontsize=9.0, fontstyle="italic", ha="center", va="center", zorder=28
    )

    ax.plot([-8.45, 8.45], [3.58, 3.58], color=PALETTE["rule_dark"], lw=0.80, zorder=15)

    # Vertical dotted drafting dividers separating the 4 columns of the time step
    for x_div in [-5.85, -2.55, 5.85]:
        ax.plot([x_div, x_div], [-2.55, 3.45], color=PALETTE["rule_light"], lw=0.85, ls=":", zorder=3)

    # =======================================================================
    # COLUMN 0 (FAR LEFT): ESTADO CONHECIDO EM t_k (3D Physical Column Icon)
    # =======================================================================
    cx_s0 = -7.15
    crisp_text(
        ax, cx_s0, 3.32,
        r"ESTADO EM $t_k$",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=9.4, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, 3.04,
        r"(Conhecido na malha $m \times n$)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.2, fontstyle="italic", ha="center", va="top", zorder=20
    )

    # 3D Axonometric Water Column Icon (directly matching Fig 1 art!)
    draw_3d_water_column_icon(
        ax, ox=cx_s0 - 0.62, oy=1.55, scale=0.88,
        lbl_z=r"$z_{i,j}^k$", lbl_u=r"$u_{i+1/2,j}^k$", lbl_v=r"$v_{i,j+1/2}^k$"
    )

    crisp_text(
        ax, cx_s0, 0.42,
        r"• Centro: elevação $z_{i,j}^k$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, 0.12,
        r"• Faces L/O: $u_{i+1/2,j}^k$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, -0.18,
        r"• Faces N/S: $v_{i,j+1/2}^k$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )

    # Horizontal hairline inside Column 0
    ax.plot([-8.25, -6.05], [-0.46, -0.46], color=PALETTE["rule_light"], lw=0.75, zorder=10)

    crisp_text(
        ax, cx_s0, -0.62,
        r"Coeficientes congelados em $t_k$:",
        color=PALETTE["amber_sub"], stroke_w=0.17,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, -0.92,
        r"$H^k = h + z^k > 0$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=8.4, ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s0, -1.28,
        r"$\gamma^k = \dfrac{g\sqrt{(u^k)^2+(v^k)^2}}{C_z^2\, H^k}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=8.4, ha="center", va="top", zorder=20
    )

    # Arrow Column 0 -> Column 1
    draw_2d_arrow(ax, (-6.02, 1.35), (-5.62, 1.35),
                  color=PALETTE["ink_primary"], lw=1.6, mutation_scale=11.5, zorder=25)

    # =======================================================================
    # COLUMN 1 (LEFT-CENTER): ETAPA 1 — ADVECÇÃO ELM (PILAR B)
    # =======================================================================
    cx_s1 = -4.20
    crisp_text(
        ax, cx_s1, 3.32,
        r"ETAPA 1 — ADVECÇÃO ELM",
        color=PALETTE["amber_sub"], stroke_w=0.18,
        fontsize=9.4, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s1, 3.04,
        r"(Pilar B: Operador Explícito $F$ — $0$ Matrizes)",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=8.2, fontstyle="italic", ha="center", va="top", zorder=20
    )

    # Classic 2x2 Grid Engraving for ELM Backtracking (like Figure 6 right panel)
    gx_e, gy_e, cs_e = cx_s1 - 0.92, 0.55, 0.92
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

    # 4 corner nodes of the interpolation cell
    for (dx_c, dy_c) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        ax.plot(gx_e + dx_c * cs_e, gy_e + dy_c * cs_e,
                marker="D", markersize=4.8, markerfacecolor=PALETTE["v_node"],
                markeredgecolor="white", markeredgewidth=0.7, zorder=16)

    p_arr_elm = (gx_e + 2 * cs_e, gy_e + 2 * cs_e)
    p_foot_elm = (gx_e + 0.52 * cs_e, gy_e + 0.46 * cs_e)
    ax.plot(*p_arr_elm, marker="o", markersize=6.2, markerfacecolor=PALETTE["z_node"],
            markeredgecolor="white", markeredgewidth=0.9, zorder=18)
    ax.plot(*p_foot_elm, marker="*", markersize=8.8, markerfacecolor=PALETTE["u_node"],
            markeredgecolor="white", markeredgewidth=0.7, zorder=18)

    # Dashed bilinear interpolation diagonals
    for (dx_c, dy_c) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        ax.plot([gx_e + dx_c * cs_e, p_foot_elm[0]],
                [gy_e + dy_c * cs_e, p_foot_elm[1]],
                color=PALETTE["v_node"], lw=0.70, ls="--", zorder=13)

    # Parametric Bezier curve for backtracking trajectory
    P0_e = np.array(p_arr_elm)
    P2_e = np.array(p_foot_elm)
    P1_e = np.array([gx_e + 0.95 * cs_e, gy_e + 1.55 * cs_e])
    s_e = np.linspace(0, 1, 60)
    curve_e = (
        ((1 - s_e) ** 2)[:, None] * P0_e
        + (2 * (1 - s_e) * s_e)[:, None] * P1_e
        + (s_e ** 2)[:, None] * P2_e
    )
    ax.plot(curve_e[:, 0], curve_e[:, 1], color=PALETTE["z_node"], lw=1.8, zorder=17)
    draw_2d_arrow(ax, tuple(curve_e[-4]), tuple(P2_e),
                  color=PALETTE["z_node"], lw=1.8, mutation_scale=10.5, zorder=17)

    for sv in [0.33, 0.66]:
        pt_s = (1 - sv) ** 2 * P0_e + 2 * (1 - sv) * sv * P1_e + (sv ** 2) * P2_e
        ax.plot(pt_s[0], pt_s[1], marker="o", markersize=4.5,
                markerfacecolor=PALETTE["amber_sub"], markeredgecolor="white",
                markeredgewidth=0.6, zorder=19)

    crisp_text(ax, gx_e + 2 * cs_e, gy_e + 2 * cs_e + 0.10, r"$(i, j)$ em $t_{k+1}$",
               color=PALETTE["z_node"], stroke_w=0.14,
               fontsize=7.8, fontweight="bold", ha="right", va="bottom", zorder=20)
    crisp_text(ax, gx_e + 1.05 * cs_e, gy_e + 1.15 * cs_e, r"$N\text{ passos }\tau$",
               color=PALETTE["amber_sub"], stroke_w=0.14, bg_clear=True, pad=0.04,
               fontsize=7.8, fontweight="bold", ha="left", va="center", zorder=20)
    crisp_text(ax, cx_s1, gy_e - 0.14, r"Pé $(i-a, j-b)$: interpolação nos 4 nós",
               color=PALETTE["v_node"], stroke_w=0.14,
               fontsize=7.9, fontweight="bold", ha="center", va="top", zorder=20)

    # Horizontal hairline inside Column 1
    ax.plot([-5.55, -2.85], [-0.46, -0.46], color=PALETTE["rule_light"], lw=0.75, zorder=10)

    crisp_text(
        ax, cx_s1, -0.62,
        r"Entrega termos advectados explícitos:",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=8.2, fontstyle="italic", ha="center", va="top", zorder=20
    )

    # Sharp monograph equation box for Fu^k, Fv^k
    draw_drafting_frame(ax, cx_s1 - 0.95, -1.42, 1.90, 0.46,
                        ec=PALETTE["amber_sub"], fc=PALETTE["mat_bg"], lw=0.95, zorder=15)
    crisp_text(
        ax, cx_s1, -1.19,
        r"$F u_{i+1/2,j}^k\;$ e $\;F v_{i,j+1/2}^k$",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=9.1, fontweight="bold", ha="center", va="center", zorder=22
    )
    crisp_text(
        ax, cx_s1, -1.56,
        r"(entram no vetor conhecido $\mathbf{b}$ da Etapa 2)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.9, fontstyle="italic", ha="center", va="top", zorder=20
    )

    # =======================================================================
    # COLUMN 2 (CENTER-RIGHT): A ENCRUZILHADA (CAMINHO 1 OU CAMINHO 2)
    # =======================================================================
    # Technical orthogonal fork from Column 1 to Upper Branch (Caminho 1) and Lower Branch (Caminho 2)
    x_fork, y_fork = -2.42, 1.35
    ax.plot([-2.82, x_fork], [y_fork, y_fork], color=PALETTE["ink_primary"], lw=1.4, zorder=18)
    ax.plot([x_fork, x_fork], [-0.85, 2.25], color=PALETTE["ink_primary"], lw=1.4, zorder=18)
    draw_2d_arrow(ax, (x_fork, 2.25), (-1.92, 2.25),
                  color=PALETTE["u_node"], lw=1.6, mutation_scale=11, zorder=22)
    draw_2d_arrow(ax, (x_fork, -0.85), (-1.92, -0.85),
                  color=PALETTE["v_node"], lw=1.6, mutation_scale=11, zorder=22)

    # Sharp diamond/square fork node "OU"
    ax.add_patch(Rectangle(
        (x_fork - 0.24, 0.68), 0.48, 0.34,
        facecolor=PALETTE["bg_canvas"], edgecolor=PALETTE["ink_primary"],
        linewidth=1.1, zorder=26
    ))
    crisp_text(
        ax, x_fork, 0.85, "OU",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=8.3, fontweight="bold", ha="center", va="center", zorder=28
    )

    # -----------------------------------------------------------------------
    # UPPER BRANCH: CAMINHO 1 — ESQUEMA PENTADIAGONAL 2D (PILAR A PURO)
    # -----------------------------------------------------------------------
    x_b1, y_b1, w_b1, h_b1 = -1.90, 0.92, 7.42, 2.48
    draw_drafting_frame(ax, x_b1, y_b1, w_b1, h_b1,
                        ec=PALETTE["u_node"], fc="#FDF9F7", lw=1.15, double_top=True, zorder=5)

    crisp_text(
        ax, x_b1 + 0.18, y_b1 + h_b1 - 0.18,
        r"CAMINHO 1 — Esquema Pentadiagonal 2D (Pilar A Puro): Simetria 2D Plena",
        color=PALETTE["u_node"], stroke_w=0.18,
        fontsize=9.1, fontweight="bold", ha="left", va="top", zorder=22
    )

    # Step 2A: 1 Global Pentadiagonal Matrix (left side of Upper Branch)
    draw_mini_pentadiag(ax, x0=-1.62, y0=1.18, size=1.36, zorder=15)

    crisp_text(
        ax, -0.02, 2.52,
        r"Etapa 2: Elevação $z^{k+1}$",
        color=PALETTE["u_node"], stroke_w=0.17,
        fontsize=8.8, fontweight="bold", ha="left", va="center", zorder=22
    )
    crisp_text(
        ax, -0.02, 2.20,
        r"1 Matriz Global $N \times N$ ($A\,\mathbf{z}^{k+1} = \mathbf{b}$)",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=8.3, fontweight="bold", ha="left", va="center", zorder=22
    )
    crisp_text(
        ax, -0.02, 1.58,
        r"• 5 diagonais (simétrica e def. positiva)" + "\n"
        + r"• Método Iterativo (PCG / SOR)" + "\n"
        + r"• Calcula todo $z_{i,j}^{k+1}$ simultaneamente",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.9, ha="left", va="center", linespacing=1.24, zorder=22
    )

    # Orthogonal arrow from Etapa 2 to Etapa 3 inside Upper Branch
    draw_2d_arrow(ax, (2.15, 1.90), (2.42, 1.90),
                  color=PALETTE["u_node"], lw=1.5, mutation_scale=10.5, zorder=22)

    # Step 3A: Widened sharp drafting frame with full-sized explicit velocity formulas!
    draw_drafting_frame(ax, 2.42, 1.06, 2.96, 1.96,
                        ec=PALETTE["z_node"], fc="#FFFFFF", lw=0.95, zorder=14)
    crisp_text(
        ax, 3.90, 2.86,
        r"Etapa 3: Velocidades ($0$ Matrizes — Conta Direta)",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.0, fontweight="bold", ha="center", va="top", zorder=22
    )
    ax.plot([2.52, 5.28], [2.58, 2.58], color=PALETTE["rule_light"], lw=0.65, zorder=15)

    # Full-sized, crystal-clear symbolic equations showing friction gamma^k and wind tau_x, tau_y!
    crisp_text(
        ax, 3.90, 2.16,
        r"$u^{k+1} = \dfrac{F u^k - g\Delta t\,\nabla_x z^{k+1} + \Delta t\,\tau_x}{1 + \Delta t\,\gamma^k}$",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=8.6, ha="center", va="center", zorder=24
    )
    crisp_text(
        ax, 3.90, 1.44,
        r"$v^{k+1} = \dfrac{F v^k - g\Delta t\,\nabla_y z^{k+1} + \Delta t\,\tau_y}{1 + \Delta t\,\gamma^k}$",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=8.6, ha="center", va="center", zorder=24
    )

    # -----------------------------------------------------------------------
    # LOWER BRANCH: CAMINHO 2 — VARIANTE ADI (PILAR C: SUBSTITUI O PILAR A)
    # -----------------------------------------------------------------------
    x_b2, y_b2, w_b2, h_b2 = -1.90, -2.55, 7.42, 3.22
    draw_drafting_frame(ax, x_b2, y_b2, w_b2, h_b2,
                        ec=PALETTE["v_node"], fc="#F7FBFA", lw=1.15, double_top=True, zorder=5)

    crisp_text(
        ax, x_b2 + 0.5 * w_b2, y_b2 + h_b2 - 0.18,
        r"CAMINHO 2 — Variante ADI (Pilar C, substitui o Pilar A): $m + n$ Sistemas Tridiagonais via Thomas $\mathcal{O}(N)$",
        color=PALETTE["v_node"], stroke_w=0.18,
        fontsize=8.7, fontweight="bold", ha="center", va="top", zorder=22
    )

    # Half-Step 1 (Left inside Lower Branch): t_k -> t_{k+1/2} (Varredura x)
    draw_drafting_frame(ax, -1.74, -2.02, 3.36, 2.22,
                        ec=PALETTE["u_node"], fc="#FFFFFF", lw=0.90, zorder=14)
    crisp_text(
        ax, -0.06, 0.06,
        r"1º Meio-Passo ($t_k \rightarrow t_{k+1/2}$): Varredura Horizontal $x$",
        color=PALETTE["u_node"], stroke_w=0.17,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=22
    )
    ax.plot([-1.64, 1.52], [-0.20, -0.20], color=PALETTE["rule_light"], lw=0.65, zorder=15)

    draw_mini_tridiag_stack(ax, x0=-1.56, y0=-1.38, size=0.88, off_col=PALETTE["u_node"], count=4, zorder=16)

    crisp_text(
        ax, -0.34, -0.52,
        r"$m$ Matrizes Tridiagonais ($n \times n$)",
        color=PALETTE["u_node"], stroke_w=0.16,
        fontsize=8.1, fontweight="bold", ha="left", va="center", zorder=24
    )
    crisp_text(
        ax, -0.34, -1.02,
        r"• 3 diagonais (Algoritmo de Thomas)" + "\n"
        + r"• Determina elevação $z^{k+1/2}$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.8, ha="left", va="center", linespacing=1.22, zorder=22
    )
    crisp_text(
        ax, -0.06, -1.78,
        r"Conta direta ($0$ matrizes): atualiza $\mathbf{u^{k+1/2}}$ (faces L/O)",
        color=PALETTE["z_node"], stroke_w=0.15,
        fontsize=7.6, fontweight="bold", ha="center", va="center", zorder=24
    )

    # Arrow from Half-Step 1 to Half-Step 2
    draw_2d_arrow(ax, (1.64, -0.92), (1.98, -0.92),
                  color=PALETTE["v_node"], lw=1.6, mutation_scale=10, zorder=22)

    # Half-Step 2 (Right inside Lower Branch): t_{k+1/2} -> t_{k+1} (Varredura y)
    draw_drafting_frame(ax, 2.00, -2.02, 3.36, 2.22,
                        ec=PALETTE["v_node"], fc="#FFFFFF", lw=0.90, zorder=14)
    crisp_text(
        ax, 3.68, 0.06,
        r"2º Meio-Passo ($t_{k+1/2} \rightarrow t_{k+1}$): Varredura Vertical $y$",
        color=PALETTE["v_node"], stroke_w=0.17,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=22
    )
    ax.plot([2.10, 5.26], [-0.20, -0.20], color=PALETTE["rule_light"], lw=0.65, zorder=15)

    draw_mini_tridiag_stack(ax, x0=2.18, y0=-1.38, size=0.88, off_col=PALETTE["v_node"], count=4, zorder=16)

    crisp_text(
        ax, 3.40, -0.52,
        r"$n$ Matrizes Tridiagonais ($m \times m$)",
        color=PALETTE["v_node"], stroke_w=0.16,
        fontsize=8.1, fontweight="bold", ha="left", va="center", zorder=24
    )
    crisp_text(
        ax, 3.40, -1.02,
        r"• 3 diagonais (Algoritmo de Thomas)" + "\n"
        + r"• Determina elevação final $z^{k+1}$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.8, ha="left", va="center", linespacing=1.22, zorder=22
    )
    crisp_text(
        ax, 3.68, -1.78,
        r"Conta direta ($0$ matrizes): atualiza $\mathbf{v^{k+1}}$ (faces N/S)",
        color=PALETTE["z_node"], stroke_w=0.15,
        fontsize=7.6, fontweight="bold", ha="center", va="center", zorder=24
    )

    # Clear explanatory footer inside ADI branch resolving the u^{k+1/2} vs u^{k+1} notation!
    crisp_text(
        ax, x_b2 + 0.5 * w_b2, -2.30,
        r"Fechamento do passo ADI em $t_{k+1}$: após a 2ª varredura, o estado completo no novo nível temporal $(z^{k+1},\, u^{k+1},\, v^{k+1})$ fica determinado.",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=7.9, fontstyle="italic", ha="center", va="center", zorder=24
    )

    # =======================================================================
    # COLUMN 3 (FAR RIGHT): NOVO ESTADO EM t_{k+1} (3D Physical Column Icon)
    # =======================================================================
    # Orthogonal convergence lines from Upper Branch and Lower Branch into Column 3
    x_join = 5.75
    ax.plot([x_b1 + w_b1, x_join], [2.25, 2.25], color=PALETTE["u_node"], lw=1.4, zorder=18)
    ax.plot([x_b2 + w_b2, x_join], [-0.85, -0.85], color=PALETTE["v_node"], lw=1.4, zorder=18)
    ax.plot([x_join, x_join], [-0.85, 2.25], color=PALETTE["z_node"], lw=1.4, zorder=18)
    draw_2d_arrow(ax, (x_join, 1.35), (6.12, 1.35),
                  color=PALETTE["z_node"], lw=1.6, mutation_scale=11.5, zorder=22)

    cx_s4 = 7.25
    crisp_text(
        ax, cx_s4, 3.32,
        r"NOVO ESTADO $t_{k+1}$",
        color=PALETTE["z_node"], stroke_w=0.18,
        fontsize=9.4, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s4, 3.04,
        r"(Previsto em $t_k + \Delta t$)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.2, fontstyle="italic", ha="center", va="top", zorder=20
    )

    # 3D Axonometric Water Column Icon for t_{k+1}
    draw_3d_water_column_icon(
        ax, ox=cx_s4 - 0.62, oy=1.55, scale=0.88,
        lbl_z=r"$z_{i,j}^{k+1}$", lbl_u=r"$u_{i+1/2,j}^{k+1}$", lbl_v=r"$v_{i,j+1/2}^{k+1}$"
    )

    crisp_text(
        ax, cx_s4, 0.42,
        r"• Nova elevação $z_{i,j}^{k+1}$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s4, 0.08,
        r"• Novas velocidades $u^{k+1},\; v^{k+1}$",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", zorder=20
    )

    ax.plot([6.15, 8.35], [-0.46, -0.46], color=PALETTE["rule_light"], lw=0.75, zorder=10)

    crisp_text(
        ax, cx_s4, -0.62,
        r"Propriedades Garantidas:",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=20
    )
    crisp_text(
        ax, cx_s4, -0.92,
        "• Estável sem limite CFL\n"
        r"   de onda rápida ($\sqrt{gH}$)" + "\n"
        "• Sem oscilação espúria\n"
        "• Conservação de volume",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.0, ha="center", va="top", linespacing=1.26, zorder=20
    )

    # =======================================================================
    # TEMPORAL FEEDBACK LOOP (SHARP ORTHOGONAL RETURN LINE: t_{k+1} -> t_k)
    # =======================================================================
    y_loop = -3.12
    ax.plot([cx_s4, cx_s4], [-2.25, y_loop], color=PALETTE["amber_sub"], lw=1.4, ls="--", zorder=18)
    ax.plot([cx_s4, cx_s0], [y_loop, y_loop], color=PALETTE["amber_sub"], lw=1.4, ls="--", zorder=18)
    draw_2d_arrow(ax, (cx_s0, y_loop), (cx_s0, -2.15),
                  color=PALETTE["amber_sub"], lw=1.5, mutation_scale=11, zorder=22)

    crisp_text(
        ax, 0.0, y_loop,
        r"Avanço do Loop Temporal ($k \leftarrow k + 1$): Recalcula coeficientes numéricos $H^k = h + z^k$ e $\gamma^k$ na matriz (padrão de esparsidade fixo)",
        color=PALETTE["amber_sub"], stroke_w=0.17, bg_clear=True, pad=0.14,
        fontsize=8.6, fontweight="bold", ha="center", va="center", zorder=26
    )

    # =======================================================================
    # BOTTOM BOOKTABS SYNTHESIS STRIP (Paper vs. Code & Matrix Count)
    # =======================================================================
    ax.plot([-8.45, 8.45], [-3.65, -3.65], color=PALETTE["rule_dark"], lw=0.80, zorder=15)

    # Left bottom note: A(W) and B(W) never enter the code
    crisp_text(
        ax, -8.35, -3.84,
        r"Nota Conceitual — Papel vs. Computador: As matrizes $3 \times 3$ $A(W)$ e $B(W)$ da Seção 0.2 nunca entram no código!",
        color=PALETTE["u_node"], stroke_w=0.17,
        fontsize=8.6, fontweight="bold", ha="left", va="top", zorder=25
    )
    crisp_text(
        ax, -8.35, -4.14,
        r"Elas servem apenas na análise teórica das características para identificar que $\nabla z$ e $\nabla\cdot\vec{u}$ geram a celeridade $c = \sqrt{gH}$.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.1, fontstyle="italic", ha="left", va="top", zorder=25
    )

    # Right bottom note: Comparison of matrix counts per time step
    crisp_text(
        ax, 8.35, -3.84,
        r"Balanço de Matrizes por Passo $\Delta t$:   Etapa 1 (ELM) $= 0$   |   Etapa 2 $= 1$ Pentadiagonal (Pilar A) OU $m+n$ Tridiagonais (Pilar C)",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.6, fontweight="bold", ha="right", va="top", zorder=25
    )
    crisp_text(
        ax, 8.35, -4.14,
        r"O Pilar C (ADI) não ocorre após o Pilar A — é um caminho alternativo que substitui a matriz pentadiagonal por varreduras 1D.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.1, fontstyle="italic", ha="right", va="top", zorder=25
    )

    # Classic bottom double rule closing the figure
    ax.plot([-8.45, 8.45], [-4.52, -4.52], color=PALETTE["rule_dark"], lw=0.55, zorder=15)
    ax.plot([-8.45, 8.45], [-4.59, -4.59], color=PALETTE["rule_dark"], lw=1.35, zorder=15)

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-8.65, 8.65)
    ax.set_ylim(-4.75, 4.70)
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
