"""
Generate an Edward Tufte-inspired vector scientific illustration explaining the
physical and mathematical meaning of the x-momentum equation in the 2D Shallow
Water Equations (2D SWE), following Casulli (1990):

    du/dt + u du/dx + v du/dy = -g dz/dx - gamma u + tau_x

Outputs:
  - ../figures/swe_momentum_x_meaning.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_momentum_x_meaning.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_momentum_x_meaning.png (high-resolution raster preview)
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Polygon, FancyArrowPatch, Rectangle, Circle
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
# 2. Edward Tufte Muted Cartographic & Oceanographic Palette (Matched to Fig 1)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FCFBF7",       # Warm archival paper ivory
    "bg_panel": "#F5F2EB",        # Soft warm stone for marginalia & equation banner
    "bg_card": "#FAF8F2",         # Subtle inset card background
    "rule_dark": "#8C8275",       # Bookplate structural rule
    "rule_light": "#D6CFC4",      # Subtle section divider
    "ink_primary": "#1E242B",     # Deep charcoal ink for primary typography
    "ink_secondary": "#485360",   # Muted slate for explanatory annotations
    "ink_muted": "#7A8490",       # Whisper-quiet gray for leader lines
    "water_fill": "#C4DFEE",      # Translucent water body fill
    "water_col": "#E6F2F8",       # Highlighted central control column
    "water_edge": "#235170",      # Crisp structural free-surface curve
    "datum_line": "#334155",      # Undisturbed reference plane z = 0
    "velocity_u": "#113852",      # Deep Prussian navy for velocity u & LHS terms
    "pressure_g": "#1D5B86",      # Rich cerulean blue for -g dz/dx & hydrostatic pressure
    "wind_tau": "#1F686B",        # Muted sea-teal for wind forcing tau_x
    "friction_gamma": "#9A3B26",  # Warm Venetian terracotta for bottom friction -gamma u
    "bed_fill": "#C8BBAE",        # Geological seabed cross-section
    "bed_edge": "#6B5B4C",        # Seabed interface curve
    "bed_hatch": "#877666",       # Fine geological sediment hatching
}


def draw_arrow(
    ax, p0, p1, color, lw=1.3, mutation_scale=11.5, arrowstyle="-|>",
    zorder=20, ls="-", alpha=1.0, connectionstyle="arc3,rad=0.0"
):
    """Draw a precision 2D vector arrow."""
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


def draw_brace_horizontal(ax, x0, x1, y, height, color, lw=0.9, zorder=22):
    """Draw a clean horizontal Tufte curly/square bracket for equation terms."""
    xm = 0.5 * (x0 + x1)
    ym = y + height
    # Smooth 3-segment architectural bracket
    ax.plot(
        [x0, x0, xm, x1, x1],
        [y, y + 0.55 * height, y + 0.55 * height, y + 0.55 * height, y],
        color=color, lw=lw, zorder=zorder
    )
    ax.plot([xm, xm], [y + 0.55 * height, ym], color=color, lw=lw, zorder=zorder)
    return xm, ym


def add_tufte_leader(
    ax, target_pt, anchor_pt, text_pt, title, lines,
    title_color=None, align="left", rad=0.14, zorder=28
):
    """Draw a Tufte callout with leader line starting outside the text block."""
    if title_color is None:
        title_color = PALETTE["ink_primary"]
    tx, ty = target_pt
    ax.plot(tx, ty, marker="o", markersize=3.3, color=title_color, zorder=zorder)
    conn = FancyArrowPatch(
        anchor_pt, target_pt,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-",
        color=PALETTE["ink_muted"],
        linewidth=0.68,
        zorder=zorder - 2,
    )
    ax.add_patch(conn)

    bx, by = text_pt
    t1 = ax.text(
        bx, by, title,
        fontsize=9.8, fontweight="bold", color=title_color,
        ha=align, va="bottom", zorder=zorder + 1
    )
    t1.set_path_effects([pe.withStroke(linewidth=3.0, foreground=PALETTE["bg_canvas"])])

    b1 = ax.text(
        bx, by - 0.08, "\n".join(lines),
        fontsize=8.7, color=PALETTE["ink_secondary"],
        ha=align, va="top", linespacing=1.32, zorder=zorder + 1
    )
    b1.set_path_effects([pe.withStroke(linewidth=3.0, foreground=PALETTE["bg_canvas"])])


def build_figure():
    fig, ax = plt.subplots(figsize=(16.6, 10.6), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # =======================================================================
    # 1. TOP BOOKPLATE HEADER & ANATOMICAL EQUATION BANNER
    # =======================================================================
    ax.text(
        0.0, 10.25,
        "Significado Físico e Dinâmico da Equação de Quantidade de Movimento na Direção $x$",
        fontsize=14.2, fontweight="bold", color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=30
    )
    ax.text(
        0.0, 9.80,
        r"Decomposição entre aceleração local, transporte advectivo no campo $(x \times y)$, gradiente de pressão hidrostática, dissipação por atrito no leito e forçamento pelo vento.",
        fontsize=9.9, fontstyle="italic", color=PALETTE["ink_secondary"],
        ha="left", va="top", zorder=30
    )
    ax.plot([0.0, 16.4], [9.44, 9.44], color=PALETTE["rule_light"], lw=0.85, zorder=28)

    # Equation Anatomy Strip
    eq_y0, eq_y1 = 7.42, 9.25
    ax.add_patch(Rectangle(
        (0.0, eq_y0), 16.4, eq_y1 - eq_y0,
        facecolor=PALETTE["bg_panel"], edgecolor="none", alpha=0.92, zorder=10
    ))
    ax.plot([0.0, 16.4], [eq_y1, eq_y1], color=PALETTE["rule_dark"], lw=0.95, zorder=12)
    ax.plot([0.0, 16.4], [eq_y0, eq_y0], color=PALETTE["rule_dark"], lw=0.75, zorder=12)

    # Term positions along the equation strip (y_eq = 8.48)
    y_eq = 8.52
    # Term 1: du/dt
    ax.text(1.55, y_eq, r"$\dfrac{\partial u}{\partial t}$", fontsize=14.0, color=PALETTE["velocity_u"], ha="center", va="center", zorder=20)
    ax.text(2.35, y_eq, r"$+$", fontsize=13.0, color=PALETTE["ink_primary"], ha="center", va="center", zorder=20)
    # Term 2: u du/dx + v du/dy
    ax.text(4.35, y_eq, r"$u\dfrac{\partial u}{\partial x} \;+\; v\dfrac{\partial u}{\partial y}$", fontsize=14.0, color=PALETTE["velocity_u"], ha="center", va="center", zorder=20)
    # Equals sign
    ax.text(6.65, y_eq, r"$=$", fontsize=14.0, color=PALETTE["ink_primary"], ha="center", va="center", zorder=20)
    # Term 3: -g dz/dx
    ax.text(8.45, y_eq, r"$-g\dfrac{\partial z}{\partial x}$", fontsize=14.0, color=PALETTE["pressure_g"], ha="center", va="center", zorder=20)
    # Term 4: -gamma u
    ax.text(11.45, y_eq, r"$-\;\gamma u$", fontsize=14.0, color=PALETTE["friction_gamma"], ha="center", va="center", zorder=20)
    # Term 5: + tau_x
    ax.text(14.35, y_eq, r"$+\;\tau_x$", fontsize=14.0, color=PALETTE["wind_tau"], ha="center", va="center", zorder=20)

    # Over-labels (Lado Esquerdo vs Lado Direito)
    ax.text(
        3.35, 9.04,
        r"LADO ESQUERDO — Taxa de Variação Total (Derivada Material $\mathrm{D}u/\mathrm{D}t$)",
        fontsize=8.7, fontweight="bold", color=PALETTE["velocity_u"], ha="center", va="center", zorder=20
    )
    ax.plot([0.85, 5.85], [8.88, 8.88], color=PALETTE["velocity_u"], lw=0.6, alpha=0.55, zorder=19)

    ax.text(
        11.45, 9.04,
        r"LADO DIREITO — Forças Horizontais por Unidade de Massa na Direção $x$",
        fontsize=8.7, fontweight="bold", color=PALETTE["ink_primary"], ha="center", va="center", zorder=20
    )
    ax.plot([7.35, 15.55], [8.88, 8.88], color=PALETTE["ink_secondary"], lw=0.6, alpha=0.55, zorder=19)

    # Under-brackets & physical descriptions for each term
    b_y = 8.12
    # Bracket 1: du/dt
    xm1, ym1 = draw_brace_horizontal(ax, 0.85, 2.15, b_y, -0.16, PALETTE["velocity_u"], lw=0.8)
    ax.text(
        xm1, ym1 - 0.06,
        "Variação temporal\nlocal de $u(x,y,t)$",
        fontsize=8.3, color=PALETTE["velocity_u"], ha="center", va="top", linespacing=1.22, zorder=20
    )

    # Bracket 2: u du/dx + v du/dy
    xm2, ym2 = draw_brace_horizontal(ax, 2.75, 5.95, b_y, -0.16, PALETTE["velocity_u"], lw=0.8)
    ax.text(
        xm2, ym2 - 0.06,
        r"Advecção espacial no campo $x \times y$" + "\n" + r"(variação $\partial u/\partial x$ e $\partial u/\partial y$)",
        fontsize=8.3, color=PALETTE["velocity_u"], ha="center", va="top", linespacing=1.22, zorder=20
    )

    # Bracket 3: -g dz/dx
    xm3, ym3 = draw_brace_horizontal(ax, 7.35, 9.55, b_y, -0.16, PALETTE["pressure_g"], lw=0.8)
    ax.text(
        xm3, ym3 - 0.06,
        r"Gradiente de pressão hidrostática:" + "\n" + r"impulsiona ($\partial z/\partial x < 0$) ou freia ($\partial z/\partial x > 0$)",
        fontsize=8.3, color=PALETTE["pressure_g"], ha="center", va="top", linespacing=1.22, zorder=20
    )

    # Bracket 4: -gamma u
    xm4, ym4 = draw_brace_horizontal(ax, 10.35, 12.55, b_y, -0.16, PALETTE["friction_gamma"], lw=0.8)
    ax.text(
        xm4, ym4 - 0.06,
        r"Dissipação por atrito com o fundo:" + "\n" + r"opõe-se ao movimento ($\gamma \geq 0$)",
        fontsize=8.3, color=PALETTE["friction_gamma"], ha="center", va="top", linespacing=1.22, zorder=20
    )

    # Bracket 5: + tau_x
    xm5, ym5 = draw_brace_horizontal(ax, 13.30, 15.45, b_y, -0.16, PALETTE["wind_tau"], lw=0.8)
    ax.text(
        xm5, ym5 - 0.06,
        r"Forçamento externo pelo vento:" + "\n" + r"acelera ($\tau_x > 0$) ou desacelera ($\tau_x < 0$)",
        fontsize=8.3, color=PALETTE["wind_tau"], ha="center", va="top", linespacing=1.22, zorder=20
    )

    # =======================================================================
    # 2. MAIN LEFT/CENTER PANEL (PAINEL I):
    #    Longitudinal Physical Mechanism in the Water Column (Plane x-z)
    # =======================================================================
    ax.text(
        0.0, 7.05,
        r"I. Mecanismo Hidrostático e Balanço de Forças na Coluna de Água — Corte Longitudinal $(x, z)$",
        fontsize=11.0, fontweight="bold", color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=25
    )
    ax.text(
        0.0, 6.72,
        r"Caso ilustrado: superfície mais alta à esquerda e mais baixa à direita ($\partial z/\partial x < 0 \;\Longrightarrow\; -g\,\partial z/\partial x > 0$, acelerando $u$ para a direita).",
        fontsize=8.9, fontstyle="italic", color=PALETTE["ink_secondary"],
        ha="left", va="top", zorder=25
    )

    # Coordinate setup for the longitudinal water channel (x from 0.6 to 9.6)
    x_ch0, x_ch1 = 0.65, 9.55
    xs = np.linspace(x_ch0, x_ch1, 200)
    xn = (xs - x_ch0) / (x_ch1 - x_ch0)

    y_datum = 4.55  # Undisturbed reference level z = 0
    # Free surface z(x,y,t): higher on the left, sloping smoothly downward to the right (dz/dx < 0)
    def z_surf_fn(x_val):
        s = (x_val - x_ch0) / (x_ch1 - x_ch0)
        return y_datum + 0.85 * np.cos(0.88 * np.pi * s) + 0.12

    # Gently sloping seabed z = -h(x,y)
    def z_bed_fn(x_val):
        s = (x_val - x_ch0) / (x_ch1 - x_ch0)
        return 1.55 + 0.22 * np.sin(1.1 * np.pi * s - 0.3)

    ys_surf = z_surf_fn(xs)
    ys_bed = z_bed_fn(xs)
    y_rock_base = 0.72

    # 2A. Water body background polygon
    ax.add_patch(Polygon(
        list(zip(np.concatenate([xs, xs[::-1]]), np.concatenate([ys_surf, ys_bed[::-1]]))),
        facecolor=PALETTE["water_fill"], edgecolor="none", alpha=0.45, zorder=3
    ))

    # 2B. Highlighted Control Volume Column [x_L, x_R] in the center of the channel
    x_L, x_R = 3.25, 6.95
    xs_col = np.linspace(x_L, x_R, 80)
    ax.add_patch(Polygon(
        list(zip(
            np.concatenate([xs_col, xs_col[::-1]]),
            np.concatenate([z_surf_fn(xs_col), z_bed_fn(xs_col[::-1])])
        )),
        facecolor=PALETTE["water_col"], edgecolor="none", alpha=0.72, zorder=4
    ))
    # Vertical control volume boundary faces at x_L and x_R
    y_surf_L, y_bed_L = z_surf_fn(x_L), z_bed_fn(x_L)
    y_surf_R, y_bed_R = z_surf_fn(x_R), z_bed_fn(x_R)
    ax.plot([x_L, x_L], [y_bed_L, y_surf_L], color=PALETTE["pressure_g"], lw=1.25, ls="-", zorder=8)
    ax.plot([x_R, x_R], [y_bed_R, y_surf_R], color=PALETTE["pressure_g"], lw=1.25, ls="-", zorder=8)

    # 2C. Geological Seabed Substratum & Tufte Hatching
    ax.add_patch(Polygon(
        list(zip(
            np.concatenate([xs, [x_ch1, x_ch0]]),
            np.concatenate([ys_bed, [y_rock_base, y_rock_base]])
        )),
        facecolor=PALETTE["bed_fill"], edgecolor="none", alpha=0.92, zorder=5
    ))
    ax.plot(xs, ys_bed, color=PALETTE["bed_edge"], lw=1.45, zorder=9)
    ax.plot([x_ch0, x_ch1], [y_rock_base, y_rock_base], color=PALETTE["rule_light"], lw=0.8, zorder=6)

    for xh in np.linspace(x_ch0 + 0.18, x_ch1 - 0.18, 42):
        for k_s in range(3):
            xs_h = xh + (k_s - 1) * 0.05
            yt_h = z_bed_fn(xs_h)
            yb_h = max(y_rock_base + 0.08, yt_h - 0.34 + 0.05 * k_s)
            ax.plot(
                [xs_h, xs_h - 0.16], [yt_h, yb_h],
                color=PALETTE["bed_hatch"], lw=0.45, alpha=0.65, zorder=6
            )

    ax.text(
        5.10, y_rock_base + 0.22,
        r"Leito marinho impermeável   $z = -h(x,y)$   (rugosidade de Chézy $C_z$)",
        fontsize=8.9, fontstyle="italic", color="#473B30", ha="center", va="center", zorder=15
    )

    # 2D. Free-Surface Curve z(x,y,t) & Undisturbed Reference Level z = 0
    ax.plot(xs, ys_surf, color=PALETTE["water_edge"], lw=1.75, zorder=10)
    ax.plot([x_ch0, x_ch1], [y_datum, y_datum], color=PALETTE["datum_line"], lw=1.0, ls=(0, (5, 3)), zorder=9)
    ax.text(
        x_ch1 - 0.08, y_datum + 0.10,
        r"Nível de referência não perturbado ($z = 0$)",
        fontsize=8.4, fontstyle="italic", color=PALETTE["datum_line"],
        ha="right", va="bottom", zorder=15
    ).set_path_effects([pe.withStroke(linewidth=2.8, foreground=PALETTE["bg_canvas"])])

    # 2E. Tangent Slope Line on Free Surface showing dz/dx < 0
    x_tan_c = 5.25
    y_tan_c = z_surf_fn(x_tan_c)
    dz_dx_num = (z_surf_fn(x_tan_c + 0.01) - z_surf_fn(x_tan_c - 0.01)) / 0.02
    # Horizontal dashed reference and sloped tangent segment
    ax.plot(
        [x_tan_c - 0.70, x_tan_c + 1.05],
        [y_tan_c - 0.70 * dz_dx_num, y_tan_c + 1.05 * dz_dx_num],
        color=PALETTE["pressure_g"], lw=1.1, ls="--", zorder=14
    )
    # Right-angle slope triangle (dx vs dz < 0)
    x_tri0 = x_tan_c - 0.20
    y_tri0 = z_surf_fn(x_tri0)
    x_tri1 = x_tri0 + 1.10
    y_tri1 = z_surf_fn(x_tri1)
    ax.plot([x_tri0, x_tri1], [y_tri0, y_tri0], color=PALETTE["pressure_g"], lw=0.8, ls=":", zorder=14)
    ax.plot([x_tri1, x_tri1], [y_tri0, y_tri1], color=PALETTE["pressure_g"], lw=0.95, zorder=14)
    ax.text(
        x_tri1 + 0.10, 0.5 * (y_tri0 + y_tri1) + 0.10,
        r"Inclinação $\dfrac{\partial z}{\partial x} < 0$" + "\n"
        + r"($z_{\mathrm{esq}} > z_{\mathrm{dir}}$)",
        fontsize=9.0, fontweight="bold", color=PALETTE["pressure_g"],
        ha="left", va="center", zorder=20
    ).set_path_effects([pe.withStroke(linewidth=3.0, foreground=PALETTE["bg_canvas"])])

    # Gravity vector g (placed cleanly on the left above the crest)
    draw_arrow(ax, (1.25, 6.40), (1.25, 5.65), color=PALETTE["ink_primary"], lw=1.6, mutation_scale=11, zorder=20)
    ax.text(
        1.38, 6.02, r"$\mathbf{g}$ (gravidade $g$)",
        fontsize=9.4, color=PALETTE["ink_primary"], ha="left", va="center", zorder=20
    )

    # 2F. Left & Right Hydrostatic Pressure Triangles (Explaining WHY -g dz/dx > 0)
    # Left face (x = x_L): Deeper column H_E -> Larger hydrostatic pressure pushing RIGHT (+x)
    w_press_L = 1.15  # wider pressure base on left
    ax.add_patch(Polygon(
        [(x_L - w_press_L, y_bed_L), (x_L, y_bed_L), (x_L, y_surf_L)],
        facecolor=PALETTE["pressure_g"], edgecolor=PALETTE["pressure_g"],
        lw=0.8, alpha=0.18, zorder=7
    ))
    ax.plot([x_L - w_press_L, x_L], [y_bed_L, y_surf_L], color=PALETTE["pressure_g"], lw=1.0, zorder=8)
    for frac in [0.20, 0.40, 0.60, 0.80, 0.95]:
        yp = y_surf_L - frac * (y_surf_L - y_bed_L)
        wp = frac * w_press_L
        draw_arrow(
            ax, (x_L - wp, yp), (x_L - 0.02, yp),
            color=PALETTE["pressure_g"], lw=0.95, mutation_scale=8.5, zorder=9
        )
    ax.text(
        x_L - 0.58, 3.88,
        r"Pressão hidrostática" + "\n" + r"à esquerda $p_E(z')$" + "\n"
        + r"$\mathbf{maior}$ ($z_E$ mais alto)",
        fontsize=8.5, color=PALETTE["pressure_g"], ha="right", va="center", zorder=18
    ).set_path_effects([pe.withStroke(linewidth=2.8, foreground="#D4E8F5")])

    # Elevation dimension z_E and depth h(x,y) near left boundary (x = 0.92)
    draw_arrow(ax, (0.92, y_datum), (0.92, z_surf_fn(0.92)), color=PALETTE["water_edge"], lw=0.95, mutation_scale=7.5, arrowstyle="<|-|>")
    ax.text(1.02, 0.5 * (y_datum + z_surf_fn(0.92)), r"$z_E > 0$", fontsize=9.2, color=PALETTE["water_edge"], ha="left", va="center", zorder=18)

    draw_arrow(ax, (0.92, z_bed_fn(0.92)), (0.92, y_datum), color=PALETTE["water_edge"], lw=0.95, mutation_scale=7.5, arrowstyle="<|-|>")
    ax.text(1.02, 0.5 * (y_datum + z_bed_fn(0.92)) - 0.15, r"$h(x,y)$", fontsize=9.2, color=PALETTE["water_edge"], ha="left", va="center", zorder=18)

    # Right face (x = x_R): Shallower column H_D -> Smaller hydrostatic pressure pushing LEFT (-x)
    w_press_R = 0.72  # narrower pressure base on right
    ax.add_patch(Polygon(
        [(x_R + w_press_R, y_bed_R), (x_R, y_bed_R), (x_R, y_surf_R)],
        facecolor=PALETTE["pressure_g"], edgecolor=PALETTE["pressure_g"],
        lw=0.8, alpha=0.18, zorder=7
    ))
    ax.plot([x_R + w_press_R, x_R], [y_bed_R, y_surf_R], color=PALETTE["pressure_g"], lw=1.0, zorder=8)
    for frac in [0.25, 0.50, 0.75, 0.95]:
        yp = y_surf_R - frac * (y_surf_R - y_bed_R)
        wp = frac * w_press_R
        draw_arrow(
            ax, (x_R + wp, yp), (x_R + 0.02, yp),
            color=PALETTE["pressure_g"], lw=0.85, mutation_scale=7.5, zorder=9
        )
    ax.text(
        x_R + w_press_R + 0.10, 0.48 * y_bed_R + 0.52 * y_surf_R,
        r"Pressão hidrostática" + "\n" + r"à direita $p_D(z')$" + "\n"
        + r"$\mathbf{menor}$ ($z_D$ mais baixo)",
        fontsize=8.6, color=PALETTE["pressure_g"], ha="left", va="center", zorder=18
    ).set_path_effects([pe.withStroke(linewidth=2.8, foreground="#D4E8F5")])

    # 2G. Inside the Control Column [x_L, x_R]: The 3 Competing Dynamical Terms + Velocity u
    x_mid = 0.5 * (x_L + x_R)  # 5.10

    # (1) Hydrostatic Pressure Gradient Acceleration: -g dz/dx > 0 (Upper-mid depth)
    y_fg = 3.68
    draw_arrow(
        ax, (x_mid - 1.15, y_fg), (x_mid + 1.25, y_fg),
        color=PALETTE["pressure_g"], lw=2.5, mutation_scale=15, zorder=18
    )
    ax.text(
        x_mid, y_fg + 0.15,
        r"Resultante hidrostática: $\;-g\dfrac{\partial z}{\partial x} > 0$",
        fontsize=10.2, fontweight="bold", color=PALETTE["pressure_g"],
        ha="center", va="bottom", zorder=22
    ).set_path_effects([pe.withStroke(linewidth=3.2, foreground=PALETTE["water_col"])])
    ax.text(
        x_mid, y_fg - 0.12,
        r"(desloca a água da coluna mais alta $z_E$ para a mais baixa $z_D$, acelerando $u$)",
        fontsize=8.3, fontstyle="italic", color=PALETTE["pressure_g"],
        ha="center", va="top", zorder=22
    ).set_path_effects([pe.withStroke(linewidth=3.0, foreground=PALETTE["water_col"])])

    # (2) Depth-Averaged Velocity u(x,y,t) (Lower-mid depth)
    y_vel = 2.75
    draw_arrow(
        ax, (x_mid - 0.95, y_vel), (x_mid + 1.05, y_vel),
        color=PALETTE["velocity_u"], lw=2.2, mutation_scale=13.5, zorder=18
    )
    ax.text(
        x_mid + 0.05, y_vel + 0.12,
        r"Velocidade média na coluna $\;u(x,y,t) > 0$",
        fontsize=9.8, fontweight="bold", color=PALETTE["velocity_u"],
        ha="center", va="bottom", zorder=22
    ).set_path_effects([pe.withStroke(linewidth=3.2, foreground=PALETTE["water_col"])])

    # (3) Bottom Friction Dissipation: -gamma u (Near seabed, opposing u!)
    y_fric = z_bed_fn(x_mid) + 0.22
    draw_arrow(
        ax, (x_mid + 1.00, y_fric), (x_mid - 0.95, y_fric),
        color=PALETTE["friction_gamma"], lw=2.15, mutation_scale=13.5, zorder=18
    )
    ax.text(
        x_mid + 0.05, y_fric + 0.12,
        r"Dissipação por atrito no fundo: $\;-\gamma u < 0\;\;(\gamma \geq 0)$",
        fontsize=9.4, fontweight="bold", color=PALETTE["friction_gamma"],
        ha="center", va="bottom", zorder=22
    ).set_path_effects([pe.withStroke(linewidth=3.2, foreground=PALETTE["water_col"])])

    # (4) Surface Wind Forcing: tau_x (Above the free surface)
    x_w0 = 3.55
    y_w0 = z_surf_fn(x_w0) + 0.34
    x_w1 = 5.30
    y_w1 = z_surf_fn(x_w1) + 0.34
    draw_arrow(
        ax, (x_w0, y_w0), (x_w1, y_w1),
        color=PALETTE["wind_tau"], lw=2.05, mutation_scale=13, zorder=18
    )
    # Subtle opposing dashed wind arrow to illustrate "podendo acelerar ou desacelerar"
    draw_arrow(
        ax, (x_w1, y_w1 + 0.20), (x_w0 + 0.55, y_w0 + 0.20),
        color=PALETTE["wind_tau"], lw=1.0, mutation_scale=8.5, ls="--", alpha=0.65, zorder=17
    )
    ax.text(
        0.5 * (x_w0 + x_w1) + 0.10, y_w0 + 0.46,
        r"Forçamento pelo vento $\;\tau_x$",
        fontsize=9.8, fontweight="bold", color=PALETTE["wind_tau"],
        ha="center", va="bottom", zorder=22
    ).set_path_effects([pe.withStroke(linewidth=3.0, foreground=PALETTE["bg_canvas"])])
    ax.text(
        0.5 * (x_w0 + x_w1) + 0.10, y_w0 + 0.25,
        r"(acelera se $\tau_x > 0$ ou freia se $\tau_x < 0$)",
        fontsize=8.3, fontstyle="italic", color=PALETTE["wind_tau"],
        ha="center", va="bottom", zorder=22
    ).set_path_effects([pe.withStroke(linewidth=3.0, foreground=PALETTE["bg_canvas"])])

    # Coordinate axes (x, z) for Panel I at bottom-left
    draw_arrow(ax, (0.35, 0.72), (0.35, 6.25), color=PALETTE["ink_primary"], lw=1.15, mutation_scale=10, zorder=20)
    ax.text(0.35, 6.32, r"$z$", fontsize=11.5, color=PALETTE["ink_primary"], ha="center", va="bottom", zorder=22)

    draw_arrow(ax, (0.35, 0.72), (9.85, 0.72), color=PALETTE["ink_primary"], lw=1.15, mutation_scale=10, zorder=20)
    ax.text(9.95, 0.72, r"$x$", fontsize=11.5, color=PALETTE["ink_primary"], ha="left", va="center", zorder=22)

    # Control column horizontal span bracket [x, x + dx] below x-axis
    ax.plot([x_L, x_L], [0.72, 0.42], color=PALETTE["ink_muted"], lw=0.7, ls=":", zorder=15)
    ax.plot([x_R, x_R], [0.72, 0.42], color=PALETTE["ink_muted"], lw=0.7, ls=":", zorder=15)
    draw_arrow(ax, (x_L, 0.46), (x_R, 0.46), color=PALETTE["ink_secondary"], lw=0.95, mutation_scale=8, arrowstyle="<|-|>")
    ax.text(x_L, 0.35, r"$x$", fontsize=9.4, color=PALETTE["ink_primary"], ha="center", va="top")
    ax.text(x_R, 0.35, r"$x + \Delta x$", fontsize=9.4, color=PALETTE["ink_primary"], ha="center", va="top")
    ax.text(
        0.5 * (x_L + x_R), 0.35,
        r"Volume de controle elementar ($\Delta x$)",
        fontsize=8.6, fontstyle="italic", color=PALETTE["ink_secondary"], ha="center", va="top"
    )

    # =======================================================================
    # 3. RIGHT-HAND TUFTE ANALYTICAL PANELS (PAINEL II & PAINEL III)
    # =======================================================================
    rx0, rx1 = 10.45, 16.40

    # -----------------------------------------------------------------------
    # PAINEL II (Top-Right): Lado Esquerdo da Equação — Mudança no Tempo e
    #                        no Campo Espacial (x * y)
    # -----------------------------------------------------------------------
    p2_y0, p2_y1 = 3.85, 7.08
    ax.add_patch(Rectangle(
        (rx0, p2_y0), rx1 - rx0, p2_y1 - p2_y0,
        facecolor=PALETTE["bg_panel"], edgecolor="none", alpha=0.92, zorder=10
    ))
    ax.plot([rx0, rx1], [p2_y1, p2_y1], color=PALETTE["rule_dark"], lw=0.95, zorder=12)
    ax.plot([rx0, rx1], [p2_y0, p2_y0], color=PALETTE["rule_light"], lw=0.75, zorder=12)

    ax.text(
        rx0 + 0.20, p2_y1 - 0.16,
        r"II. Lado Esquerdo: Mudança Temporal e Espacial no Plano $(x \times y)$",
        fontsize=9.8, fontweight="bold", color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=20
    )
    ax.text(
        rx0 + 0.20, p2_y1 - 0.44,
        r"$\dfrac{\partial u}{\partial t} \;+\; u\dfrac{\partial u}{\partial x} \;+\; v\dfrac{\partial u}{\partial y} \;=\; \dfrac{\mathrm{D}u}{\mathrm{D}t}$  (derivada material acompanhando a partícula fluida)",
        fontsize=8.5, color=PALETTE["velocity_u"],
        ha="left", va="top", zorder=20
    )

    # Draw 2D Spatial Field Grid (x * y) inside Panel II
    gx0, gx1 = rx0 + 0.55, rx0 + 3.55
    gy0, gy1 = p2_y0 + 0.35, p2_y0 + 1.88
    ax.add_patch(Rectangle(
        (gx0, gy0), gx1 - gx0, gy1 - gy0,
        facecolor=PALETTE["bg_card"], edgecolor=PALETTE["rule_light"], lw=0.8, zorder=13
    ))
    # Subtle grid lines representing the x * y spatial field
    for xv_g in np.linspace(gx0 + 0.6, gx1 - 0.6, 4):
        ax.plot([xv_g, xv_g], [gy0, gy1], color="#E2DDD3", lw=0.5, zorder=14)
    for yv_g in np.linspace(gy0 + 0.38, gy1 - 0.38, 3):
        ax.plot([gx0, gx1], [yv_g, yv_g], color="#E2DDD3", lw=0.5, zorder=14)

    # Axes for the x * y mini-map
    draw_arrow(ax, (gx0, gy0), (gx1 + 0.22, gy0), color=PALETTE["ink_primary"], lw=0.9, mutation_scale=8, zorder=16)
    ax.text(gx1 + 0.28, gy0, r"$x$", fontsize=9.2, color=PALETTE["ink_primary"], ha="left", va="center", zorder=18)
    draw_arrow(ax, (gx0, gy0), (gx0, gy1 + 0.18), color=PALETTE["ink_primary"], lw=0.9, mutation_scale=8, zorder=16)
    ax.text(gx0, gy1 + 0.22, r"$y$", fontsize=9.2, color=PALETTE["ink_primary"], ha="center", va="bottom", zorder=18)

    # Velocity field u(x,y) arrows increasing along x (du/dx) and along y (du/dy)
    # Row 1 (lower y): shorter u arrows
    draw_arrow(ax, (gx0 + 0.30, gy0 + 0.42), (gx0 + 0.85, gy0 + 0.42), color=PALETTE["velocity_u"], lw=1.2, mutation_scale=8, alpha=0.65, zorder=17)
    draw_arrow(ax, (gx0 + 1.55, gy0 + 0.42), (gx0 + 2.45, gy0 + 0.42), color=PALETTE["velocity_u"], lw=1.4, mutation_scale=9, alpha=0.82, zorder=17)
    ax.text(gx0 + 1.50, gy0 + 0.15, r"Variação em $x$: $u\,\partial u/\partial x$", fontsize=8.0, color=PALETTE["velocity_u"], ha="center", va="center", zorder=19)

    # Row 2 (higher y): longer u arrows + transverse transport v
    draw_arrow(ax, (gx0 + 0.30, gy0 + 1.18), (gx0 + 1.15, gy0 + 1.18), color=PALETTE["velocity_u"], lw=1.4, mutation_scale=9, alpha=0.82, zorder=17)
    draw_arrow(ax, (gx0 + 1.55, gy0 + 1.18), (gx0 + 2.75, gy0 + 1.18), color=PALETTE["velocity_u"], lw=1.75, mutation_scale=10.5, zorder=17)

    # Transverse v arrow carrying fluid across y
    draw_arrow(ax, (gx0 + 1.40, gy0 + 0.50), (gx0 + 1.40, gy0 + 1.08), color="#2A6F73", lw=1.25, mutation_scale=8.5, ls="-", zorder=18)
    ax.text(gx0 + 1.32, gy0 + 0.79, r"$v\dfrac{\partial u}{\partial y}$", fontsize=8.2, color="#1F585B", ha="right", va="center", zorder=19)

    # Right side of Panel II: Explanatory bullet notes for du/dt, du/dx, du/dy
    nx_txt = gx1 + 0.42
    ax.text(
        nx_txt, gy1 + 0.12,
        r"$\bullet$ Mudança temporal ($\partial u/\partial t$):",
        fontsize=8.5, fontweight="bold", color=PALETTE["velocity_u"], ha="left", va="top", zorder=20
    )
    ax.text(
        nx_txt + 0.12, gy1 - 0.16,
        "Taxa de aceleração local medida\nem um ponto fixo $(x,y)$.",
        fontsize=8.0, color=PALETTE["ink_secondary"], ha="left", va="top", linespacing=1.25, zorder=20
    )

    ax.text(
        nx_txt, gy1 - 0.68,
        r"$\bullet$ Campo espacial ($x \times y$):",
        fontsize=8.5, fontweight="bold", color=PALETTE["velocity_u"], ha="left", va="top", zorder=20
    )
    ax.text(
        nx_txt + 0.12, gy1 - 0.96,
        r"$u\,\partial u/\partial x$: transporte longitudinal" + "\n"
        + r"da variação de $u$ ao longo de $x$." + "\n"
        + r"$v\,\partial u/\partial y$: transporte transversal" + "\n"
        + r"de $u$ pelo escoamento $v$ em $y$.",
        fontsize=8.0, color=PALETTE["ink_secondary"], ha="left", va="top", linespacing=1.26, zorder=20
    )

    # -----------------------------------------------------------------------
    # PAINEL III (Bottom-Right): Efeito do Sinal da Inclinação dz/dx
    #                            (Impulso vs. Frenagem Hidrostática)
    # -----------------------------------------------------------------------
    p3_y0, p3_y1 = 0.25, 3.55
    ax.add_patch(Rectangle(
        (rx0, p3_y0), rx1 - rx0, p3_y1 - p3_y0,
        facecolor=PALETTE["bg_panel"], edgecolor="none", alpha=0.92, zorder=10
    ))
    ax.plot([rx0, rx1], [p3_y1, p3_y1], color=PALETTE["rule_dark"], lw=0.95, zorder=12)
    ax.plot([rx0, rx1], [p3_y0, p3_y0], color=PALETTE["rule_dark"], lw=0.80, zorder=12)

    ax.text(
        rx0 + 0.20, p3_y1 - 0.18,
        r"III. Papel do Sinal da Inclinação $\partial z/\partial x$: Impulso vs. Frenagem",
        fontsize=9.8, fontweight="bold", color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=20
    )

    # Two side-by-side mini cards inside Panel III
    c_w = 2.65
    c_y0, c_y1 = p3_y0 + 0.25, p3_y1 - 0.56
    c1_x0 = rx0 + 0.22
    c2_x0 = rx0 + 3.08

    for cx0, is_accel in [(c1_x0, True), (c2_x0, False)]:
        ax.add_patch(Rectangle(
            (cx0, c_y0), c_w, c_y1 - c_y0,
            facecolor=PALETTE["bg_card"], edgecolor=PALETTE["rule_light"], lw=0.8, zorder=13
        ))
        x_m = np.linspace(cx0 + 0.22, cx0 + c_w - 0.22, 60)
        sn_m = (x_m - x_m[0]) / (x_m[-1] - x_m[0])
        yd_m = c_y0 + 1.24
        yb_m = c_y0 + 0.48

        if is_accel:
            # Higher on left, lower on right: dz/dx < 0 -> -g dz/dx > 0 (accelerates u > 0)
            ys_m = yd_m + 0.24 * (1.0 - 2.0 * sn_m)
            title_c = r"Caso A: $\;\partial z/\partial x < 0$"
            sub_c = r"$\Longrightarrow\;-g\,\partial z/\partial x > 0$ (Impulsiona)"
            col_force = PALETTE["pressure_g"]
        else:
            # Lower on left, higher on right: dz/dx > 0 -> -g dz/dx < 0 (brakes u > 0)
            ys_m = yd_m + 0.24 * (2.0 * sn_m - 1.0)
            title_c = r"Caso B: $\;\partial z/\partial x > 0$"
            sub_c = r"$\Longrightarrow\;-g\,\partial z/\partial x < 0$ (Freia)"
            col_force = PALETTE["friction_gamma"]

        ax.text(cx0 + 0.14, c_y1 - 0.14, title_c, fontsize=8.7, fontweight="bold", color=PALETTE["ink_primary"], ha="left", va="top", zorder=18)
        ax.text(cx0 + 0.14, c_y1 - 0.44, sub_c, fontsize=8.2, fontweight="bold", color=col_force, ha="left", va="top", zorder=18)

        # Mini water fill & bed
        ax.add_patch(Polygon(
            list(zip(np.concatenate([x_m, [x_m[-1], x_m[0]]]), np.concatenate([ys_m, [yb_m, yb_m]]))),
            facecolor=PALETTE["water_fill"], edgecolor="none", alpha=0.52, zorder=14
        ))
        ax.plot(x_m, ys_m, color=PALETTE["water_edge"], lw=1.35, zorder=16)
        ax.plot([x_m[0], x_m[-1]], [yd_m, yd_m], color=PALETTE["datum_line"], lw=0.75, ls="--", zorder=15)
        ax.plot([x_m[0], x_m[-1]], [yb_m, yb_m], color=PALETTE["bed_edge"], lw=1.15, zorder=16)

        # Velocity u arrow (always moving right, u > 0)
        xc_mid = 0.5 * (x_m[0] + x_m[-1])
        draw_arrow(
            ax, (xc_mid - 0.55, yb_m + 0.26), (xc_mid + 0.55, yb_m + 0.26),
            color=PALETTE["velocity_u"], lw=1.35, mutation_scale=8.5, zorder=18
        )
        ax.text(xc_mid, yb_m + 0.34, r"$u > 0$", fontsize=8.0, color=PALETTE["velocity_u"], ha="center", va="bottom", zorder=19)

        # Hydrostatic force arrow -g dz/dx
        if is_accel:
            draw_arrow(
                ax, (xc_mid - 0.55, yb_m + 0.68), (xc_mid + 0.55, yb_m + 0.68),
                color=col_force, lw=1.65, mutation_scale=9.5, zorder=18
            )
            note_str = "Superfície mais alta à esq.:\ngravidade acelera $u$ para $+x$."
        else:
            draw_arrow(
                ax, (xc_mid + 0.55, yb_m + 0.68), (xc_mid - 0.55, yb_m + 0.68),
                color=col_force, lw=1.65, mutation_scale=9.5, zorder=18
            )
            note_str = "Superfície mais alta à dir.:\ngradiente opõe-se e freia $u$."

        ax.text(
            xc_mid, c_y0 + 0.08, note_str,
            fontsize=7.8, color=PALETTE["ink_secondary"],
            ha="center", va="bottom", linespacing=1.22, zorder=19
        )

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-0.15, 16.55)
    ax.set_ylim(0.05, 10.45)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.15)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_momentum_x_meaning.svg"
    pdf_path = out_dir / "swe_momentum_x_meaning.pdf"
    png_path = out_dir / "swe_momentum_x_meaning.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
