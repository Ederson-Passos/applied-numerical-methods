"""
Generate an Edward Tufte-inspired vector scientific illustration comparing
(1) Explicit Upwind Advection vs. (2) Casulli's Eulerian-Lagrangian Method (ELM)
for Pillar B of the Semi-Implicit Finite Difference Scheme in the 2D Shallow
Water Equations (2D SWE), following Casulli (1990).

Spacious two-panel side-by-side comparative layout on warm archival paper (#FCFBF7),
matching Figure 5's exact aesthetic, color palette, and razor-sharp LaTeX Latin
Modern Roman & Computer Modern Math typography (self-colored micro-stroke reinforcement).
Maximally visual ("falar muito com pouco texto"):

Left Panel:
  1. Upwind Explícito (Estabilidade Condicional e Difusão Artificial):
     - Top: 2D Spatial Grid (i-2, i-1, i) showing a fluid particle starting 2 cells
       upstream (inside cell [i-3, i-2]) at t_k and arriving at node (i, j) at t_{k+1}
       when Courant > 1, while the fixed Upwind stencil only looks 1 cell back (at i-1),
       missing the true origin and causing numerical explosion (CFL violation).
     - Bottom: Visual wave front comparison showing how 1st-order truncation error
       (artificial viscosity) smears/diffuses sharp physical fronts.

Right Panel:
  2. Método Euleriano-Lagrangiana — ELM (Rastreamento + Interpolação Bilinear):
     - Large 2D Spatial Grid (i-2, i-1, i) x (j-2, j-1, j) showing:
         * Step 1 & 2 (Backtracking in N sub-steps tau = dt/N): Starting at arrival
           node (i, j) at t_{k+1} and integrating dx/dt = u, dy/dt = v backward in time
           along a curved streamline through N = 4 sub-steps tau to the exact foot of
           the characteristic (i - a, j - b) at t_k.
         * Step 3 (Bilinear Interpolation): The cell [i-2, i-1] x [j-2, j-1]
           containing (i - a, j - b) highlighted with its 4 surrounding corner nodes
           and fractional distances (p, 1-p) and (q, 1-q), showing the convex weighted
           average (|f| <= 1, unconditionally stable for any dt).

Outputs:
  - ../figures/swe_elm_vs_upwind.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_elm_vs_upwind.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_elm_vs_upwind.png (high-resolution raster preview)
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, FancyArrowPatch
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
    "ink_muted": "#687380",       # Clean slate gray for leader lines & grid axes
    "rule_light": "#D6CFC4",      # Subtle divider rule
    "water_high": "#A9CFE5",      # High water / sharp physical wave fill
    "water_low": "#D6EAF5",       # Low water / bilinear cell highlight
    "water_edge": "#1E4966",      # Crisp structural water edge
    "cell_bg": "#F3EFEA",         # Subtle archival cell interior
    "cell_focus": "#E8F1F6",      # Highlighted interpolation cell
    "cell_alert": "#F9EBEB",      # Soft warning tint for upwind stencil blind cell
    "cell_border": "#4A5968",     # Crisp cell boundary
    "z_node": "#145374",          # Deep cerulean for arrival node & ELM trajectory
    "u_node": "#8E321E",          # Deep Venetian terracotta for upwind error / foot point
    "v_node": "#17575A",          # Deep sea-teal for 4 bilinear interpolation nodes
    "amber_sub": "#B06D1E",       # Warm ochre/amber for temporal sub-steps tau
    "stream_col": "#88A6BC",      # Subtle background streamline arrows
    "bed_edge": "#5E4F41",        # Baseline border
}


def crisp_text(ax, x, y, s, color="#11161C", stroke_w=0.16, bg_pill=None, pad=0.14, **kwargs):
    """
    Render razor-sharp LaTeX text by reinforcing ultra-thin Computer Modern
    hairlines with a micro self-colored stroke (no blurry halo!).
    """
    if bg_pill is not None:
        kwargs["bbox"] = dict(
            boxstyle=f"round,pad={pad}",
            facecolor=bg_pill,
            edgecolor="none",
            alpha=0.92,
        )
    t = ax.text(x, y, s, color=color, **kwargs)
    if stroke_w > 0:
        t.set_path_effects([pe.withStroke(linewidth=stroke_w, foreground=color)])
    return t


def draw_2d_arrow(
    ax, p0, p1, color, lw=1.4, mutation_scale=11.5, arrowstyle="-|>",
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


def build_figure():
    fig, ax = plt.subplots(figsize=(15.6, 8.9), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # Vertical dashed divider separating Left Panel (Upwind) and Right Panel (ELM)
    ax.plot([0.0, 0.0], [-4.65, 4.45], color=PALETTE["rule_light"], lw=0.95, ls="--", zorder=3)

    # =======================================================================
    # LEFT PANEL: EXPLICIT UPWIND (CFL VIOLATION & ARTIFICIAL DIFFUSION)
    # =======================================================================
    xc_L = -4.55

    # Panel 1 Title & Concise Mathematical Condition
    crisp_text(
        ax, xc_L, 4.25,
        r"1. Upwind Explícito: Limite de 1 Célula (CFL) e Difusão Artificial",
        color=PALETTE["u_node"], stroke_w=0.20,
        fontsize=11.0, fontweight="bold", ha="center", va="bottom", zorder=28
    )
    crisp_text(
        ax, xc_L, 4.00,
        r"Estêncil fixo olha apenas para $i-1$ $\;\Longrightarrow\;$ exige $\Delta t \leq \left(\dfrac{|u|}{\Delta x} + \dfrac{|v|}{\Delta y}\right)^{-1}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=9.3, ha="center", va="top", zorder=28
    )

    # -----------------------------------------------------------------------
    # Left Top: 2D Grid showing Particle Coming from 2 Cells Back vs. Stencil at i-1
    # -----------------------------------------------------------------------
    x_nodes_L = [-7.75, -5.65, -3.55, -1.45]  # i-3, i-2, i-1, i
    y_nodes_L = [0.15, 1.45, 2.75]            # j-1, j, j+1
    x_lbls_L = [r"$i - 3$", r"$i - 2$", r"$i - 1$", r"$i$"]
    y_lbls_L = [r"$j - 1$", r"$j$", r"$j + 1$"]

    # Fill background cells
    for ix in range(3):
        for iy in range(2):
            xl, xr = x_nodes_L[ix], x_nodes_L[ix + 1]
            yb, yt = y_nodes_L[iy], y_nodes_L[iy + 1]
            if ix == 2 and iy == 0:
                fc = PALETTE["cell_alert"]   # Stencil only looks here (1 cell back)
            elif ix == 0 and iy == 0:
                fc = "#EBF3F7"               # True origin cell (> 1 cell back)
            else:
                fc = PALETTE["cell_bg"]
            ax.add_patch(Rectangle(
                (xl, yb), xr - xl, yt - yb,
                facecolor=fc, edgecolor=PALETTE["cell_border"],
                linewidth=1.0, linestyle="-", alpha=0.88, zorder=4
            ))

    # Subtle background velocity field vectors
    for gx in np.linspace(-7.2, -2.0, 4):
        for gy in [0.55, 1.10, 1.85, 2.35]:
            draw_2d_arrow(
                ax, (gx - 0.22, gy - 0.08), (gx + 0.22, gy + 0.08),
                color=PALETTE["stream_col"], lw=0.85, mutation_scale=7.5,
                alpha=0.55, zorder=5
            )

    # Grid node dots and index labels
    for ix, xv in enumerate(x_nodes_L):
        crisp_text(
            ax, xv, y_nodes_L[0] - 0.16, x_lbls_L[ix],
            color=PALETTE["ink_secondary"], stroke_w=0.15,
            fontsize=8.9, fontweight="bold", ha="center", va="top", zorder=15
        )
        for iy, yv in enumerate(y_nodes_L):
            ax.plot(xv, yv, marker="o", markersize=5.0,
                    markerfacecolor=PALETTE["ink_muted"], markeredgecolor="white",
                    markeredgewidth=0.8, zorder=10)

    for iy, yv in enumerate(y_nodes_L):
        crisp_text(
            ax, x_nodes_L[0] - 0.18, yv, y_lbls_L[iy],
            color=PALETTE["ink_secondary"], stroke_w=0.15,
            fontsize=8.9, fontweight="bold", ha="right", va="center", zorder=15
        )

    # Arrival node (i, j) at t_{k+1}
    P_arr_L = (x_nodes_L[3], y_nodes_L[1])  # (i, j)
    ax.plot(*P_arr_L, marker="o", markersize=8.5,
            markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
            markeredgewidth=1.3, zorder=22)
    crisp_text(
        ax, P_arr_L[0] + 0.14, P_arr_L[1] + 0.08,
        r"Nó $(i, j)$" + "\n" + r"em $t_{k+1}$",
        color=PALETTE["z_node"], stroke_w=0.18, bg_pill=PALETTE["bg_canvas"],
        fontsize=8.8, fontweight="bold", ha="left", va="center", zorder=25
    )

    # Upwind neighbor nodes (i-1, j) and (i, j-1) that the stencil looks at
    P_up_x = (x_nodes_L[2], y_nodes_L[1])   # (i-1, j)
    P_up_y = (x_nodes_L[3], y_nodes_L[0])   # (i, j-1)
    for pt in [P_up_x, P_up_y]:
        ax.plot(*pt, marker="s", markersize=7.2,
                markerfacecolor=PALETTE["u_node"], markeredgecolor="white",
                markeredgewidth=1.1, zorder=21)

    # Short rigid Upwind stencil arrows (1 cell only: i-1 -> i and j-1 -> j)
    draw_2d_arrow(
        ax, (P_up_x[0] + 0.12, P_up_x[1]), (P_arr_L[0] - 0.14, P_arr_L[1]),
        color=PALETTE["u_node"], lw=2.3, mutation_scale=12, zorder=20
    )
    draw_2d_arrow(
        ax, (P_up_y[0], P_up_y[1] + 0.12), (P_arr_L[0], P_arr_L[1] - 0.14),
        color=PALETTE["u_node"], lw=1.8, mutation_scale=10.5, ls="--", zorder=20
    )

    crisp_text(
        ax, 0.5 * (P_up_x[0] + P_arr_L[0]), P_up_x[1] + 0.18,
        r"Estêncil Upwind" + "\n" + r"(olha só $i-1$)",
        color=PALETTE["u_node"], stroke_w=0.17, bg_pill=PALETTE["cell_alert"], pad=0.10,
        fontsize=8.3, fontweight="bold", ha="center", va="bottom", linespacing=1.15, zorder=24
    )

    # True Fluid Particle Origin > 2 cells back (inside cell [i-3, i-2] x [j-1, j])
    P_true_L = (-6.85, 0.52)
    ax.plot(*P_true_L, marker="o", markersize=8.5,
            markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
            markeredgewidth=1.3, zorder=22)

    # Long curved trajectory of the real particle crossing > 2 cells in dt
    # Using rad=0.18 so the arc curves BELOW row j and never overlaps node (i-1, j)!
    draw_2d_arrow(
        ax, P_true_L, (P_arr_L[0] - 0.14, P_arr_L[1] - 0.10),
        color=PALETTE["z_node"], lw=2.2, mutation_scale=13,
        ls="--", connectionstyle="arc3,rad=0.16", zorder=19
    )

    crisp_text(
        ax, P_true_L[0] + 0.10, P_true_L[1] + 0.30,
        r"Origem real em $t_k$" + "\n" + r"(2+ células atrás!)",
        color=PALETTE["z_node"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.4, fontweight="bold", ha="center", va="bottom", linespacing=1.15, zorder=25
    )

    # Label along the true particle trajectory
    crisp_text(
        ax, -4.75, 0.62,
        r"Trajetória real da partícula em $\Delta t$",
        color=PALETTE["z_node"], stroke_w=0.15, bg_pill=PALETTE["bg_canvas"], pad=0.08,
        fontsize=8.1, fontstyle="italic", ha="center", va="center", zorder=23
    )

    # Callout badge above grid showing the blind gap ("Fora do alcance do estêncil -> explode!")
    draw_2d_arrow(
        ax, (P_true_L[0], 3.12), (P_up_x[0], 3.12),
        color=PALETTE["u_node"], lw=1.5, mutation_scale=10.5, arrowstyle="<|-|>", zorder=22
    )
    ax.plot([P_true_L[0], P_true_L[0]], [P_true_L[1] + 0.85, 3.18],
            color=PALETTE["u_node"], lw=0.85, ls=":", zorder=12)
    ax.plot([P_up_x[0], P_up_x[0]], [P_up_x[1] + 0.12, 3.18],
            color=PALETTE["u_node"], lw=0.85, ls=":", zorder=12)

    crisp_text(
        ax, 0.5 * (P_true_L[0] + P_up_x[0]), 3.24,
        r"Fora do estêncil ($\mathrm{CFL} > 1$) $\;\Longrightarrow\;$ instabilidade!",
        color=PALETTE["u_node"], stroke_w=0.18, bg_pill=PALETTE["cell_alert"], pad=0.12,
        fontsize=8.7, fontweight="bold", ha="center", va="bottom", zorder=25
    )

    # -----------------------------------------------------------------------
    # Left Bottom: Visual Demonstration of Artificial Numerical Diffusion
    # -----------------------------------------------------------------------
    ax.plot([-8.45, -0.55], [-0.48, -0.48], color=PALETTE["rule_light"], lw=0.80, zorder=5)

    crisp_text(
        ax, xc_L, -0.70,
        r"Efeito da 1ª Ordem ($\mathrm{CFL} \leq 1$): Difusão Numérica Artificial (Viscosidade Falsa)",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=9.6, fontweight="bold", ha="center", va="top", zorder=25
    )

    # Mini wave plot comparing Exact Sharp Wave vs Upwind Diffused/Smeared Wave
    xw = np.linspace(-7.95, -1.15, 320)
    xc_wave = -4.55
    y_wbase = -3.45

    # Exact sharp physical wave front
    y_exact = y_wbase + 1.55 * np.exp(-((xw - xc_wave) / 0.58) ** 4)
    # Upwind diffused wave
    y_upwind = y_wbase + 0.86 * np.exp(-((xw - xc_wave) / 1.48) ** 2)

    # Baseline
    ax.plot([-8.10, -1.00], [y_wbase, y_wbase], color=PALETTE["bed_edge"], lw=1.15, zorder=8)

    # Fill under exact wave
    ax.fill_between(
        xw, y_wbase, y_exact,
        color=PALETTE["water_high"], alpha=0.45, zorder=5
    )
    ax.plot(xw, y_exact, color=PALETTE["z_node"], lw=2.0, ls="-", zorder=12)

    # Fill & curve for diffused upwind wave
    ax.fill_between(
        xw, y_wbase, y_upwind,
        color="#E8C5B8", alpha=0.45, zorder=6
    )
    ax.plot(xw, y_upwind, color=PALETTE["u_node"], lw=2.2, ls="--", zorder=14)

    # Vertical amplitude loss arrow at wave crest
    y_top_ex = y_wbase + 1.55
    y_top_up = y_wbase + 0.86
    draw_2d_arrow(
        ax, (xc_wave, y_top_ex - 0.04), (xc_wave, y_top_up + 0.04),
        color=PALETTE["u_node"], lw=1.6, mutation_scale=10.5, zorder=18
    )

    # Lateral smearing arrows
    draw_2d_arrow(
        ax, (xc_wave - 0.65, y_wbase + 0.42), (xc_wave - 1.45, y_wbase + 0.42),
        color=PALETTE["u_node"], lw=1.3, mutation_scale=9.5, zorder=18
    )
    draw_2d_arrow(
        ax, (xc_wave + 0.65, y_wbase + 0.42), (xc_wave + 1.45, y_wbase + 0.42),
        color=PALETTE["u_node"], lw=1.3, mutation_scale=9.5, zorder=18
    )

    # Concise direct labels on the wave profiles
    crisp_text(
        ax, xc_wave - 0.58, y_top_ex - 0.05,
        "Frente física real\n(nitidez melhor preservada pelo ELM)",
        color=PALETTE["z_node"], stroke_w=0.16,
        fontsize=8.4, fontweight="bold", ha="right", va="top", linespacing=1.18, zorder=22
    )
    crisp_text(
        ax, xc_wave + 0.95, y_top_up + 0.18,
        "Upwind Explícito\n(\"borra\" e amortece a onda)",
        color=PALETTE["u_node"], stroke_w=0.16,
        fontsize=8.4, fontweight="bold", ha="left", va="bottom", linespacing=1.18, zorder=22
    )

    crisp_text(
        ax, xc_L, y_wbase - 0.25,
        r"Erro de 1ª ordem introduz viscosidade artificial $\;\propto |u|\,\Delta x\,\dfrac{\partial^2 u}{\partial x^2}\;$ que achata picos e frentes",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.4, fontstyle="italic", ha="center", va="top", zorder=22
    )

    # =======================================================================
    # RIGHT PANEL: EULERIAN-LAGRANGIAN METHOD (ELM)
    # =======================================================================
    xc_R = 4.75

    # Panel 2 Title & Concise Mathematical Invariant
    crisp_text(
        ax, xc_R, 4.25,
        r"2. Método Euleriano-Lagrangiano (ELM): Rastreamento e Interpolação",
        color=PALETTE["z_node"], stroke_w=0.20,
        fontsize=11.0, fontweight="bold", ha="center", va="bottom", zorder=28
    )
    crisp_text(
        ax, xc_R, 4.00,
        r"Invariante $\dfrac{\mathrm{d}w}{\mathrm{d}t} = 0$ ao longo de $\dfrac{\mathrm{d}x}{\mathrm{d}t} = u,\; \dfrac{\mathrm{d}y}{\mathrm{d}t} = v$ $\;\Longrightarrow\;$ incondicionalmente estável ($|f| \leq 1, \;\forall \Delta t$)",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=9.3, ha="center", va="top", zorder=28
    )

    # -----------------------------------------------------------------------
    # Right Main Canvas: 2D Spatial Grid with Backtracking (N sub-steps tau)
    # and Enlarged Bilinear Interpolation Cell at the Foot (i-a, j-b)
    # -----------------------------------------------------------------------
    x_nodes_R = [1.05, 3.70, 6.35]    # i-2, i-1, i
    y_nodes_R = [-2.65, 0.05, 2.75]   # j-2, j-1, j
    x_lbls_R = [r"$i - 2$", r"$i - 1$", r"$i$"]
    y_lbls_R = [r"$j - 2$", r"$j - 1$", r"$j$"]

    # Draw the 4 grid cells
    for ix in range(2):
        for iy in range(2):
            xl, xr = x_nodes_R[ix], x_nodes_R[ix + 1]
            yb, yt = y_nodes_R[iy], y_nodes_R[iy + 1]
            if ix == 0 and iy == 0:
                fc = PALETTE["cell_focus"]
                ec = PALETTE["v_node"]
                lw_c = 1.85
            else:
                fc = PALETTE["cell_bg"]
                ec = PALETTE["cell_border"]
                lw_c = 1.00
            ax.add_patch(Rectangle(
                (xl, yb), xr - xl, yt - yb,
                facecolor=fc, edgecolor=ec,
                linewidth=lw_c, zorder=4 if not (ix == 0 and iy == 0) else 6
            ))

    # Subtle background curved velocity field vectors
    for gx in [1.7, 3.0, 4.35, 5.65]:
        for gy in [-2.0, -0.7, 0.7, 2.0]:
            ang = 0.25 + 0.08 * (gx - 1.0)
            dx_v = 0.24 * np.cos(ang)
            dy_v = 0.24 * np.sin(ang)
            draw_2d_arrow(
                ax, (gx - dx_v, gy - dy_v), (gx + dx_v, gy + dy_v),
                color=PALETTE["stream_col"], lw=0.85, mutation_scale=7.5,
                alpha=0.50, zorder=5
            )

    # Regular grid nodes & column headers
    for ix, xv in enumerate(x_nodes_R):
        crisp_text(
            ax, xv, y_nodes_R[2] + 0.18, x_lbls_R[ix],
            color=PALETTE["ink_secondary"], stroke_w=0.16,
            fontsize=9.2, fontweight="bold", ha="center", va="bottom", zorder=15
        )
        for iy, yv in enumerate(y_nodes_R):
            ax.plot(xv, yv, marker="o", markersize=5.2,
                    markerfacecolor=PALETTE["ink_muted"], markeredgecolor="white",
                    markeredgewidth=0.8, zorder=10)

    # Row labels placed cleanly to the left of the vertical brackets so they never touch
    for iy, yv in enumerate(y_nodes_R):
        x_row_lbl = x_nodes_R[0] - 0.56 if iy < 2 else x_nodes_R[0] - 0.18
        crisp_text(
            ax, x_row_lbl, yv, y_lbls_R[iy],
            color=PALETTE["ink_secondary"], stroke_w=0.16,
            fontsize=9.2, fontweight="bold", ha="right", va="center", zorder=15
        )

    # -----------------------------------------------------------------------
    # Step 1 & 2: Arrival Node (i, j) at t_{k+1} and Backtracking in N=4 sub-steps tau
    # -----------------------------------------------------------------------
    P_start = np.array([x_nodes_R[2], y_nodes_R[2]])  # (i, j) = (6.35, 2.75)
    # Foot of characteristic inside bottom-left cell [i-2, i-1] x [j-2, j-1]
    W_c = x_nodes_R[1] - x_nodes_R[0]
    H_c = y_nodes_R[1] - y_nodes_R[0]
    P_foot = np.array([x_nodes_R[0] + 0.56 * W_c, y_nodes_R[0] + 0.54 * H_c])

    # Parametric smooth curved streamline from P_start (s=0) back to P_foot (s=1)
    def char_curve(s):
        s_arr = np.asarray(s)
        P_ctrl = np.array([3.55, 1.75])
        return (
            ((1 - s_arr) ** 2)[:, None] * P_start
            + (2 * (1 - s_arr) * s_arr)[:, None] * P_ctrl
            + (s_arr ** 2)[:, None] * P_foot
        )

    # Draw continuous physical streamline in subtle dashed cerulean
    s_fine = np.linspace(0, 1, 120)
    pts_fine = char_curve(s_fine)
    ax.plot(pts_fine[:, 0], pts_fine[:, 1],
            color=PALETTE["z_node"], lw=1.4, ls=":", alpha=0.75, zorder=15)

    # N = 4 sub-steps tau = dt / N along the curve
    N_sub = 4
    s_nodes = np.linspace(0, 1, N_sub + 1)
    pts_sub = char_curve(s_nodes)

    for k in range(N_sub):
        pA = pts_sub[k]
        pB = pts_sub[k + 1]
        draw_2d_arrow(
            ax, tuple(pA), tuple(pB),
            color=PALETTE["z_node"], lw=2.35, mutation_scale=12.5,
            connectionstyle="arc3,rad=0.05", zorder=21
        )
        if k > 0:
            ax.plot(pA[0], pA[1], marker="o", markersize=6.2,
                    markerfacecolor=PALETTE["amber_sub"], markeredgecolor="white",
                    markeredgewidth=1.0, zorder=23)

        # Label each sub-step tau_k cleanly to the upper-left of the curve
        pm = 0.5 * (pA + pB)
        offsets_tau = [(-0.18, 0.25), (-0.28, 0.22), (-0.30, 0.16), (-0.28, 0.12)]
        dx_t, dy_t = offsets_tau[k]
        crisp_text(
            ax, pm[0] + dx_t, pm[1] + dy_t,
            rf"$\tau_{k+1}$",
            color=PALETTE["amber_sub"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.08,
            fontsize=8.6, fontweight="bold", ha="center", va="center", zorder=24
        )

    # Arrival node (i, j) marker at t_{k+1}
    ax.plot(P_start[0], P_start[1], marker="o", markersize=9.2,
            markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
            markeredgewidth=1.4, zorder=26)

    # Callout 1: Placed in upper-left cell [i-2, i-1] x [j-1, j] with leader arrow to (i, j)
    p_lbl_start = (2.38, 2.25)
    draw_2d_arrow(
        ax, (3.55, 2.38), (P_start[0] - 0.16, P_start[1] - 0.03),
        color=PALETTE["z_node"], lw=1.05, mutation_scale=9,
        connectionstyle="arc3,rad=-0.10", zorder=26
    )
    crisp_text(
        ax, p_lbl_start[0], p_lbl_start[1],
        r"1. Nó de chegada $(i, j)$ em $t_{k+1}$" + "\n"
        + r"(início do rastreamento)",
        color=PALETTE["z_node"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.12,
        fontsize=8.3, fontweight="bold", ha="center", va="center", linespacing=1.18, zorder=27
    )

    # Callout 2: Placed inside the upper-right cell [i-1, i] x [j-1, j], with linespacing for fractions
    crisp_text(
        ax, 5.15, 0.95,
        r"2. Rastreamento ($\Delta t = N\tau$)" + "\n"
        + r"para trás em $N$ sub-passos:" + "\n"
        + r"$\dfrac{\mathrm{d}x}{\mathrm{d}t}=u,\; \dfrac{\mathrm{d}y}{\mathrm{d}t}=v$",
        color=PALETTE["amber_sub"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.12,
        fontsize=8.2, fontweight="bold", ha="center", va="center", linespacing=1.42, zorder=26
    )

    # -----------------------------------------------------------------------
    # Step 3: Foot of the Characteristic (i - a, j - b) & 4-Node Bilinear Interpolation
    # -----------------------------------------------------------------------
    ax.plot(P_foot[0], P_foot[1], marker="*", markersize=12.5,
            markerfacecolor=PALETTE["u_node"], markeredgecolor="white",
            markeredgewidth=1.0, zorder=28)

    # Place foot label inside the right neighbor cell [i-1, i] x [j-2, j-1] with a clean leader arrow
    p_lbl_foot = (3.92, -1.19)
    draw_2d_arrow(
        ax, (p_lbl_foot[0] - 0.06, p_lbl_foot[1]), (P_foot[0] + 0.14, P_foot[1]),
        color=PALETTE["u_node"], lw=1.2, mutation_scale=9.5, zorder=26
    )
    crisp_text(
        ax, p_lbl_foot[0], p_lbl_foot[1],
        r"Pé da característica" + "\n" + r"$(i - a,\, j - b)$ em $t_k$",
        color=PALETTE["u_node"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.4, fontweight="bold", ha="left", va="center", linespacing=1.15, zorder=27
    )

    # 4 surrounding corner nodes of the interpolation cell [i-2, i-1] x [j-2, j-1]
    xl_c, xr_c = x_nodes_R[0], x_nodes_R[1]
    yb_c, yt_c = y_nodes_R[0], y_nodes_R[1]

    for (cx, cy) in [
        (xl_c, yb_c),
        (xr_c, yb_c),
        (xl_c, yt_c),
        (xr_c, yt_c),
    ]:
        ax.plot(cx, cy, marker="D", markersize=7.5,
                markerfacecolor=PALETTE["v_node"], markeredgecolor="white",
                markeredgewidth=1.1, zorder=25)
        ax.plot([cx, P_foot[0]], [cy, P_foot[1]],
                color=PALETTE["v_node"], lw=1.15, ls="--", alpha=0.80, zorder=16)

    # Internal crosshair inside cell [i-2, i-1] x [j-2, j-1] showing bilinear weights
    ax.plot([xl_c, xr_c], [P_foot[1], P_foot[1]],
            color=PALETTE["v_node"], lw=1.0, ls=":", zorder=14)
    ax.plot([P_foot[0], P_foot[0]], [yb_c, yt_c],
            color=PALETTE["v_node"], lw=1.0, ls=":", zorder=14)

    # Fractional weight brackets around the interpolation cell
    y_wbrk = yb_c - 0.24
    draw_2d_arrow(
        ax, (xl_c, y_wbrk), (P_foot[0], y_wbrk),
        color=PALETTE["v_node"], lw=1.1, mutation_scale=8.5, arrowstyle="<|-|>", zorder=20
    )
    draw_2d_arrow(
        ax, (P_foot[0], y_wbrk), (xr_c, y_wbrk),
        color=PALETTE["v_node"], lw=1.1, mutation_scale=8.5, arrowstyle="<|-|>", zorder=20
    )
    crisp_text(
        ax, 0.5 * (xl_c + P_foot[0]), y_wbrk - 0.08, r"$1 - p$",
        color=PALETTE["v_node"], stroke_w=0.15,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=22
    )
    crisp_text(
        ax, 0.5 * (P_foot[0] + xr_c), y_wbrk - 0.08, r"$p$",
        color=PALETTE["v_node"], stroke_w=0.15,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=22
    )

    x_hbrk = xl_c - 0.22
    draw_2d_arrow(
        ax, (x_hbrk, yb_c), (x_hbrk, P_foot[1]),
        color=PALETTE["v_node"], lw=1.1, mutation_scale=8.5, arrowstyle="<|-|>", zorder=20
    )
    draw_2d_arrow(
        ax, (x_hbrk, P_foot[1]), (x_hbrk, yt_c),
        color=PALETTE["v_node"], lw=1.1, mutation_scale=8.5, arrowstyle="<|-|>", zorder=20
    )
    crisp_text(
        ax, x_hbrk - 0.08, 0.5 * (yb_c + P_foot[1]), r"$1 - q$",
        color=PALETTE["v_node"], stroke_w=0.15,
        fontsize=8.3, fontweight="bold", ha="right", va="center", zorder=22
    )
    crisp_text(
        ax, x_hbrk - 0.08, 0.5 * (P_foot[1] + yt_c), r"$q$",
        color=PALETTE["v_node"], stroke_w=0.15,
        fontsize=8.3, fontweight="bold", ha="right", va="center", zorder=22
    )

    # Label below the interpolation cell
    crisp_text(
        ax, 0.5 * (xl_c + xr_c), yb_c - 0.65,
        r"3. Interpolação Bilinear nos 4 nós vizinhos" + "\n"
        + r"(média ponderada convexa $\;\Longrightarrow\;$ sem oscilações espúrias)",
        color=PALETTE["v_node"], stroke_w=0.16,
        fontsize=8.5, fontweight="bold", ha="center", va="top", linespacing=1.20, zorder=25
    )

    # -----------------------------------------------------------------------
    # Right-Side Legend & Visual Summary Column (Minimal Text, High Clarity)
    # -----------------------------------------------------------------------
    x_leg_R = 6.75

    # Item 1: Backtracking
    ax.plot(x_leg_R, 2.25, marker="o", markersize=7.8,
            markerfacecolor=PALETTE["z_node"], markeredgecolor="white", markeredgewidth=1.1, zorder=25)
    crisp_text(
        ax, x_leg_R + 0.22, 2.25,
        r"Rastreamento ($t_{k+1} \rightarrow t_k$):",
        color=PALETTE["z_node"], stroke_w=0.18,
        fontsize=9.1, fontweight="bold", ha="left", va="center", zorder=25
    )
    crisp_text(
        ax, x_leg_R + 0.22, 2.04,
        "Parte do nó fixo $(i, j)$ e descobre\n"
        "de onde veio a partícula fluida,\n"
        "podendo cruzar várias células.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.2, ha="left", va="top", linespacing=1.22, zorder=25
    )

    # Item 2: Sub-steps tau = dt / N
    ax.plot(x_leg_R, 0.65, marker="o", markersize=6.8,
            markerfacecolor=PALETTE["amber_sub"], markeredgecolor="white", markeredgewidth=1.0, zorder=25)
    crisp_text(
        ax, x_leg_R + 0.22, 0.65,
        r"Sub-passos ($\tau = \Delta t / N$):",
        color=PALETTE["amber_sub"], stroke_w=0.18,
        fontsize=9.1, fontweight="bold", ha="left", va="center", zorder=25
    )
    crisp_text(
        ax, x_leg_R + 0.22, 0.44,
        "Divide $\\Delta t$ em $N$ trechos para\n"
        "acompanhar a curvatura real\n"
        "das linhas de corrente.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.2, ha="left", va="top", linespacing=1.22, zorder=25
    )

    # Item 3: Foot of Characteristic & 4-node Bilinear Interpolation
    ax.plot(x_leg_R, -0.95, marker="D", markersize=6.8,
            markerfacecolor=PALETTE["v_node"], markeredgecolor="white", markeredgewidth=1.0, zorder=25)
    crisp_text(
        ax, x_leg_R + 0.22, -0.95,
        r"Interpolação nos 4 nós:",
        color=PALETTE["v_node"], stroke_w=0.18,
        fontsize=9.1, fontweight="bold", ha="left", va="center", zorder=25
    )
    crisp_text(
        ax, x_leg_R + 0.22, -1.16,
        r"No pé $(i-a, j-b)$, pondera os" + "\n"
        r"4 cantos da célula em $t_k$." + "\n"
        r"Por von Neumann: $|f| \leq 1$.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.2, ha="left", va="top", linespacing=1.22, zorder=25
    )

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-8.65, 9.75)
    ax.set_ylim(-4.35, 4.65)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.12)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_elm_vs_upwind.svg"
    pdf_path = out_dir / "swe_elm_vs_upwind.pdf"
    png_path = out_dir / "swe_elm_vs_upwind.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
