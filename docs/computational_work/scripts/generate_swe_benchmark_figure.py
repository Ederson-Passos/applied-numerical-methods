"""
Generate an authentic 1980s/1990s Journal of Computational Physics / Edward Tufte
scientific monograph vector illustration of Casulli's (1990) Tidal Propagation
Benchmark Domain (Section 6: M_2 Semidiurnal Tide in a Shallow Basin with a Deep
Central Channel) and Quantitative Performance Synthesis.

Inherits the exact editorial aesthetic of Figure 1 (swe_physical_domain.svg):
  - Soft warm cream/ivory archival background (#FAF8F3)
  - Fine dark graphite technical lines and LaTeX Latin Modern Roman & Computer
    Modern Math typography (self-colored micro-stroke reinforcement)
  - Controlled palette: deep navy blue, translucent ice-blue water & surface mesh,
    hatched sand-beige geological seabed cross-section, sea-teal (ADI), Venetian
    terracotta (caution/limit), and soft amber (12h solar/celestial arc).

Composition in Two Integrated Blocks:
  1. MAIN SCENE (CENTER-TOP): 3D Isometric Cutaway Block (same angle & finish as Fig 1):
     - Rectangular shallow basin: length 6000 m x width 3000 m, flat shallow bed h = 0.5 m.
     - Deep central navigation channel cutting longitudinally: width 300 m, depth h = 5 m
       (didactic vertical exaggeration in the front cross-section highlighting the step
       from 0.5 m to 5 m in the hatched sand-beige seabed).
     - Translucent free surface with fine rectangular mesh (60 x 120 cells, dx = dy = 50 m).
     - Semidiurnal Tide Physics (M_2):
         * At the front open channel entrance: incoming sinusoidal tidal wave with
           vertical dimension "a = 0,4 m" around z = 0, plus curved navy/cerulean
           arrows showing water advancing up the deep channel and spreading laterally
           onto the shallow flats.
         * Subtle closed-boundary markers (u_n = 0) on the other 3 lateral/back margins.
     - 12-Hour Celestial Arc (above the 3D basin):
         * Dashed soft-amber arc crossing from left to right over the basin:
           Left (nascente): stylized minimalist sun + "t = 0 h"
           Top (zênite): stylized sun + "t = 6 h"
           Right (poente): stylized sun + "t = 12 h"
         * Discrete label along the arc: "Ciclo semidiurno M_2: T = 12 h (720 passos de dt = 60 s)".

  2. BOTTOM QUANTITATIVE SYNTHESIS STRIP (4 compact monograph cards side-by-side):
     - Card 1 (Navy Blue): "Quebra CFL (Canal h = 5 m)" -> mini bar comparison:
       Explícito (C_r <= 1) vs. Casulli (C_r = 8, >= 8x passo maior).
     - Card 2 (Sea-Teal): "CPU CRAY X-MP/48 (1 ciclo)" -> proportional horizontal bars:
       Pentadiagonal 79 s vs. ADI 32 s (-60% tempo | 99% concordância em dt = 60 s).
     - Card 3 (Slate Blue): "Massa & Regime Permanente" -> mini chart of 2 identical
       overlapping curves: "t = 108 h approx t = 120 h (4 casas decimais | massa conservada)".
     - Card 4 (Terracotta): "Limite do ADI" -> discrete caution icon + visual divergence:
       "dt = 360 s -> erro direcional até 10% vs. 2D acoplado".

Outputs:
  - ../figures/swe_casulli_benchmark.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_casulli_benchmark.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_casulli_benchmark.png (high-resolution raster preview)
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch, Circle
from matplotlib.colors import LinearSegmentedColormap
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
    "bg_canvas": "#FAF8F3",       # Soft cream/ivory archival background requested
    "ink_primary": "#11161C",     # Deep obsidian/graphite ink for titles & math
    "ink_secondary": "#222B35",   # Crisp dark charcoal for labels
    "ink_muted": "#626E7A",       # Slate gray for dimension lines & subtle notes
    "rule_dark": "#283648",       # Classic booktabs heavy rule
    "rule_light": "#C8BBAE",      # Subtle archival divider rule
    "navy_deep": "#0D3149",       # Deep Prussian navy (titles, deep channel, axes)
    "z_node": "#145374",          # Cerulean navy
    "slate_blue": "#2B486B",      # Slate blue for Card 3
    "water_front": "#A9CCE0",     # Front-left water column face (from Fig 1)
    "water_right": "#8EB8D1",     # Front-right water column face (from Fig 1)
    "water_top": "#D6EAF5",       # Translucent ice-blue water surface
    "water_channel": "#5B92B5",   # Deeper water tint over the central 5 m channel
    "water_edge": "#204B69",      # Crisp structural water edge
    "water_mesh": "#4A7C9B",      # Fine wave mesh lines
    "bed_top": "#DFD5C7",         # Shallow flat seabed surface (h = 0.5 m)
    "bed_chan_top": "#9E8D7B",    # Deep channel seabed bottom (h = 5.0 m)
    "bed_chan_wall": "#B5A695",   # Vertical side wall of deep channel
    "bed_front": "#C8BBAE",       # Geological cross-section front face (from Fig 1)
    "bed_right": "#B3A494",       # Geological cross-section right face (from Fig 1)
    "bed_edge": "#5E4F41",        # Seabed contour & outline
    "bed_hatch": "#827161",       # Fine geological sediment hatching (from Fig 1)
    "teal_adi": "#17575A",        # Sea-teal for ADI
    "terracotta": "#8E321E",      # Venetian terracotta for alert/restriction
    "amber_sun": "#A86518",       # Soft warm amber for 12h celestial arc & sun
    "card_bg": "#F5F2EB",         # Subtle monograph card background
}


def crisp_text(ax, x, y, s, color="#11161C", stroke_w=0.16, bg_clear=False, bg_color=None, pad=0.08, **kwargs):
    """
    Render razor-sharp LaTeX text by reinforcing ultra-thin Computer Modern
    hairlines with a micro self-colored stroke (no blurry halo!).
    """
    if bg_clear or bg_color is not None:
        fc = bg_color if bg_color is not None else PALETTE["bg_canvas"]
        kwargs["bbox"] = dict(
            boxstyle=f"square,pad={pad}",
            facecolor=fc,
            edgecolor="none",
            alpha=0.94,
        )
    t = ax.text(x, y, s, color=color, **kwargs)
    if stroke_w > 0:
        t.set_path_effects([pe.withStroke(linewidth=stroke_w, foreground=color)])
    return t


def draw_2d_arrow(
    ax, p0, p1, color, lw=1.30, mutation_scale=10.5, arrowstyle="-|>",
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


def draw_drafting_frame(ax, x, y, w, h, ec="#4A5968", fc="none", lw=0.95, ls="-", double_top=False, zorder=4):
    """Draw a classic 1980s/90s sharp-cornered technical monograph frame."""
    ax.add_patch(Rectangle(
        (x, y), w, h,
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=zorder
    ))
    if double_top:
        ax.plot([x, x + w], [y + h - 0.06, y + h - 0.06],
                color=ec, lw=0.55, zorder=zorder + 1)


def draw_stylized_sun(ax, cx, cy, r_core=0.13, r_in=0.18, r_out=0.28, color="#A86518", zorder=25):
    """Draw a classic 1980s astronomical/scientific vector sun icon."""
    ax.add_patch(Circle(
        (cx, cy), r_core,
        facecolor="#FDF6E7", edgecolor=color, linewidth=1.25, zorder=zorder
    ))
    for k in range(12):
        ang = k * (2.0 * np.pi / 12.0)
        r_tip = r_out if k % 2 == 0 else 0.5 * (r_in + r_out)
        ax.plot(
            [cx + r_in * np.cos(ang), cx + r_tip * np.cos(ang)],
            [cy + r_in * np.sin(ang), cy + r_tip * np.sin(ang)],
            color=color, lw=0.95, zorder=zorder - 1
        )


# ---------------------------------------------------------------------------
# 3. 3D Axonometric Projection & Benchmark Geometry (Casulli 1990, Section 6)
#    - Expanded basin filling the canvas width!
#    - Channel width (300 m) is visually MUCH WIDER than channel depth (5 m):
#      width = 1.68 units vs. depth = 0.56 units (3:1 wide-and-shallow aspect
#      ratio, while still clearly stepping down from h = 0.5 m to h = 5.0 m).
# ---------------------------------------------------------------------------
WY = 7.40         # Basin width 3000 m expanded to fill canvas
LX = 10.20        # Basin length 6000 m expanded to fill canvas
XC_L = 2.86       # Deep channel left bank
XC_R = 4.54       # Deep channel right bank (width = 1.68 units >> depth 0.56 units!)

Z_DATUM = 0.00    # Undisturbed water level z = 0
Z_SHALLOW = -0.16 # Shallow basin bed h = 0.5 m
Z_DEEP = -0.58    # Deep central channel bed h = 5.0 m (width 1.68 is ~3x the depth 0.58!)
Z_BASE = -1.18    # Bottom of hatched geological block

angle_x = np.deg2rad(-15.0)
angle_y = np.deg2rad(25.5)
scale_x = 1.00
scale_y = 0.68
scale_z = 1.00

EX = np.array([scale_x * np.cos(angle_x), scale_x * np.sin(angle_x)])
EY = np.array([scale_y * np.cos(angle_y), scale_y * np.sin(angle_y)])
EZ = np.array([0.0, scale_z])

ORIGIN_2D = (-4.25, 0.35)


def proj(x, y, z):
    """Project 3D coordinates (x, y, z) to 2D canvas coordinates (X, Y)."""
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    z_arr = np.asarray(z)
    X = ORIGIN_2D[0] + x_arr * EX[0] + y_arr * EY[0] + z_arr * EZ[0]
    Y = ORIGIN_2D[1] + x_arr * EX[1] + y_arr * EY[1] + z_arr * EZ[1]
    return X, Y


def draw_3d_arrow(
    ax, p_start, p_end, color, lw=1.35, mutation_scale=11.5, arrowstyle="-|>",
    zorder=20, ls="-", alpha=1.0, connectionstyle="arc3,rad=0.0"
):
    x0, y0 = proj(*p_start)
    x1, y1 = proj(*p_end)
    arr = FancyArrowPatch(
        (x0, y0), (x1, y1),
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


def free_surface_z(x, y):
    """
    Visibly undulating 2D tidal wave surface z(x, y, t) entering through the
    front channel (y = 0, x in [XC_L, XC_R]) with amplitude a = 0.4 m and
    propagating along the deep channel while spreading laterally into the
    shallow basin with realistic 2D gravity-wave undulations.
    """
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    xc_mid = 0.5 * (XC_L + XC_R)
    r_lat = np.abs(x_arr - xc_mid) / (0.5 * WY)
    phase_main = 2.65 * np.pi * (y_arr / LX) + 1.35 * np.pi * (r_lat ** 1.2)
    atten = np.exp(-0.15 * (y_arr / LX) - 0.18 * r_lat)
    # Secondary harmonic ripple for visible 3D free-surface undulation (matching Fig 1!)
    ripple = 0.065 * np.sin(3.4 * np.pi * (y_arr / LX) - 1.5 * np.pi * (x_arr / WY) + 0.5)
    return 0.21 * np.cos(phase_main) * atten + ripple


def build_figure():
    fig, ax = plt.subplots(figsize=(16.0, 9.6), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # =======================================================================
    # 1. MAIN SCENE (CENTER-TOP): 3D ISOMETRIC CUTAWAY BENCHMARK DOMAIN
    # =======================================================================

    # -----------------------------------------------------------------------
    # LAYER 1: Submerged Bathymetry Surfaces (Shallow Flats h=0.5m & Deep Channel h=5m)
    # -----------------------------------------------------------------------
    # Left shallow shelf top surface: x in [0, XC_L], y in [0, LX], z = Z_SHALLOW
    pts_shelf_L = [
        proj(0, 0, Z_SHALLOW), proj(XC_L, 0, Z_SHALLOW),
        proj(XC_L, LX, Z_SHALLOW), proj(0, LX, Z_SHALLOW)
    ]
    ax.add_patch(Polygon(
        pts_shelf_L, closed=True,
        facecolor=PALETTE["bed_top"], edgecolor=PALETTE["bed_edge"],
        lw=0.80, alpha=0.92, zorder=3
    ))

    # Right shallow shelf top surface: x in [XC_R, WY], y in [0, LX], z = Z_SHALLOW
    pts_shelf_R = [
        proj(XC_R, 0, Z_SHALLOW), proj(WY, 0, Z_SHALLOW),
        proj(WY, LX, Z_SHALLOW), proj(XC_R, LX, Z_SHALLOW)
    ]
    ax.add_patch(Polygon(
        pts_shelf_R, closed=True,
        facecolor=PALETTE["bed_top"], edgecolor=PALETTE["bed_edge"],
        lw=0.80, alpha=0.92, zorder=3
    ))

    # Deep channel inner vertical wall (left side visible in axonometric view: x = XC_L)
    pts_wall_L = [
        proj(XC_L, 0, Z_DEEP), proj(XC_L, LX, Z_DEEP),
        proj(XC_L, LX, Z_SHALLOW), proj(XC_L, 0, Z_SHALLOW)
    ]
    ax.add_patch(Polygon(
        pts_wall_L, closed=True,
        facecolor=PALETTE["bed_chan_wall"], edgecolor=PALETTE["bed_edge"],
        lw=0.80, alpha=0.95, zorder=3.5
    ))

    # Deep channel bottom floor: x in [XC_L, XC_R], y in [0, LX], z = Z_DEEP
    pts_chan_bot = [
        proj(XC_L, 0, Z_DEEP), proj(XC_R, 0, Z_DEEP),
        proj(XC_R, LX, Z_DEEP), proj(XC_L, LX, Z_DEEP)
    ]
    ax.add_patch(Polygon(
        pts_chan_bot, closed=True,
        facecolor=PALETTE["bed_chan_top"], edgecolor=PALETTE["bed_edge"],
        lw=0.85, alpha=0.95, zorder=3.8
    ))

    # Subtle bathymetric grid lines on the seabed floor
    for y_b in np.linspace(0, LX, 13):
        ax.plot(*proj([0, XC_L], [y_b, y_b], [Z_SHALLOW, Z_SHALLOW]),
                color=PALETTE["bed_edge"], lw=0.35, alpha=0.35, zorder=4)
        ax.plot(*proj([XC_R, WY], [y_b, y_b], [Z_SHALLOW, Z_SHALLOW]),
                color=PALETTE["bed_edge"], lw=0.35, alpha=0.35, zorder=4)
        ax.plot(*proj([XC_L, XC_R], [y_b, y_b], [Z_DEEP, Z_DEEP]),
                color=PALETTE["bed_edge"], lw=0.38, alpha=0.45, zorder=4)

    # Back walls of the water domain (x = 0 and y = LX) with closed boundary markers (u_n = 0)
    ny_pts = 80
    nx_pts = 60
    yg = np.linspace(0, LX, ny_pts)
    xg = np.linspace(0, WY, nx_pts)

    ax.plot(*proj(np.zeros(ny_pts), yg, free_surface_z(0, yg)),
            color=PALETTE["water_edge"], lw=0.85, alpha=0.55, zorder=5)
    ax.plot(*proj(xg, np.full(nx_pts, LX), free_surface_z(xg, LX)),
            color=PALETTE["water_edge"], lw=0.85, alpha=0.55, zorder=5)
    ax.plot(*proj([0, 0], [LX, LX], [Z_SHALLOW, free_surface_z(0, LX)]),
            color=PALETTE["water_edge"], lw=0.65, ls=":", alpha=0.50, zorder=5)

    # Subtle hatch ticks along back & lateral closed boundaries indicating "Margem fechada (u_n = 0)"
    for y_ht in np.linspace(0.6, LX - 0.4, 14):
        z_ht = free_surface_z(0, y_ht)
        ax.plot(*proj([0, -0.16], [y_ht, y_ht - 0.14], [z_ht, z_ht + 0.06]),
                color=PALETTE["bed_edge"], lw=0.60, alpha=0.65, zorder=18)
    for x_ht in np.linspace(0.4, WY - 0.4, 12):
        z_ht = free_surface_z(x_ht, LX)
        ax.plot(*proj([x_ht, x_ht - 0.12], [LX, LX + 0.18], [z_ht, z_ht + 0.06]),
                color=PALETTE["bed_edge"], lw=0.60, alpha=0.65, zorder=18)

    # -----------------------------------------------------------------------
    # LAYER 2: Front-Left Stepped Geological Cutaway (y = 0) & Front-Right Face (x = WY)
    #          with exact Figure 1 sediment hatching!
    # -----------------------------------------------------------------------
    # Stepped front seabed polygon (y = 0):
    # (0, Z_SHALLOW) -> (XC_L, Z_SHALLOW) -> (XC_L, Z_DEEP) -> (XC_R, Z_DEEP)
    # -> (XC_R, Z_SHALLOW) -> (WY, Z_SHALLOW) -> (WY, Z_BASE) -> (0, Z_BASE)
    stepped_front_3d = [
        (0, 0, Z_SHALLOW),
        (XC_L, 0, Z_SHALLOW),
        (XC_L, 0, Z_DEEP),
        (XC_R, 0, Z_DEEP),
        (XC_R, 0, Z_SHALLOW),
        (WY, 0, Z_SHALLOW),
        (WY, 0, Z_BASE),
        (0, 0, Z_BASE),
    ]
    pts_bed_fl = [proj(*p) for p in stepped_front_3d]
    ax.add_patch(Polygon(
        pts_bed_fl, closed=True,
        facecolor=PALETTE["bed_front"], edgecolor=PALETTE["bed_edge"],
        lw=1.10, alpha=0.97, zorder=12
    ))

    # Fine geological sediment hatching on Front-Left Seabed Face (matching Fig 1!)
    def front_bed_top_z(x_val):
        if XC_L < x_val < XC_R:
            return Z_DEEP
        return Z_SHALLOW

    for xh in np.linspace(0.20, WY - 0.18, 38):
        for k_sub in range(3):
            dx_s = (k_sub - 1) * 0.05
            x_s = np.clip(xh + dx_s, 0.08, WY - 0.08)
            # Avoid crossing the vertical channel step walls
            if abs(x_s - XC_L) < 0.12 or abs(x_s - XC_R) < 0.12:
                continue
            zt = front_bed_top_z(x_s)
            zb = max(Z_BASE + 0.05, zt - 0.24 + 0.04 * k_sub)
            ax.plot(
                *proj([x_s, x_s - 0.12], [0, 0], [zt, zb]),
                color=PALETTE["bed_hatch"], lw=0.50, alpha=0.70, zorder=12.5
            )

    # Also hatch deeper sediment layer beneath the shallow shelves
    for xh in np.concatenate([np.linspace(0.25, XC_L - 0.22, 12), np.linspace(XC_R + 0.22, WY - 0.20, 12)]):
        for z_layer in [-0.48, -0.82]:
            ax.plot(
                *proj([xh, xh - 0.12], [0, 0], [z_layer, z_layer - 0.20]),
                color=PALETTE["bed_hatch"], lw=0.45, alpha=0.55, zorder=12.5
            )

    # Front-Right Geological Face (x = WY, y in [0, LX]): shallow bed h = 0.5 m
    pts_bed_fr = [
        proj(WY, 0, Z_SHALLOW),
        proj(WY, LX, Z_SHALLOW),
        proj(WY, LX, Z_BASE),
        proj(WY, 0, Z_BASE),
    ]
    ax.add_patch(Polygon(
        pts_bed_fr, closed=True,
        facecolor=PALETTE["bed_right"], edgecolor=PALETTE["bed_edge"],
        lw=1.05, alpha=0.97, zorder=12
    ))

    for yh in np.linspace(0.30, LX - 0.30, 34):
        for k_sub in range(3):
            dy_s = (k_sub - 1) * 0.06
            y_s = np.clip(yh + dy_s, 0.08, LX - 0.08)
            zt = Z_SHALLOW
            zb = max(Z_BASE + 0.05, zt - 0.26 + 0.04 * k_sub)
            ax.plot(
                *proj([WY, WY], [y_s, y_s - 0.14], [zt, zb]),
                color="#736354", lw=0.50, alpha=0.68, zorder=12.5
            )
        for z_layer in [-0.52, -0.85]:
            ax.plot(
                *proj([WY, WY], [yh, yh - 0.14], [z_layer, z_layer - 0.20]),
                color="#736354", lw=0.45, alpha=0.50, zorder=12.5
            )

    # -----------------------------------------------------------------------
    # LAYER 3: Translucent Front Water Cross-Section (Stepped Water Column!)
    # -----------------------------------------------------------------------
    # Left shallow water front face
    xg_L = np.linspace(0, XC_L, 25)
    pts_wat_fl_L = (
        [proj(x_, 0, free_surface_z(x_, 0)) for x_ in xg_L]
        + [proj(XC_L, 0, Z_SHALLOW), proj(0, 0, Z_SHALLOW)]
    )
    ax.add_patch(Polygon(
        pts_wat_fl_L, closed=True,
        facecolor=PALETTE["water_front"], edgecolor="none", alpha=0.42, zorder=13
    ))

    # Right shallow water front face
    xg_R = np.linspace(XC_R, WY, 25)
    pts_wat_fl_R = (
        [proj(x_, 0, free_surface_z(x_, 0)) for x_ in xg_R]
        + [proj(WY, 0, Z_SHALLOW), proj(XC_R, 0, Z_SHALLOW)]
    )
    ax.add_patch(Polygon(
        pts_wat_fl_R, closed=True,
        facecolor=PALETTE["water_front"], edgecolor="none", alpha=0.42, zorder=13
    ))

    # Central deep channel water front face (deeper Prussian/cerulean tint!)
    xg_C = np.linspace(XC_L, XC_R, 20)
    pts_wat_fl_C = (
        [proj(x_, 0, free_surface_z(x_, 0)) for x_ in xg_C]
        + [proj(XC_R, 0, Z_DEEP), proj(XC_L, 0, Z_DEEP)]
    )
    ax.add_patch(Polygon(
        pts_wat_fl_C, closed=True,
        facecolor=PALETTE["water_channel"], edgecolor="none", alpha=0.56, zorder=13.2
    ))

    # Front-Right Water Face (x = WY, y in [0, LX])
    pts_wat_fr = (
        [proj(WY, y_, free_surface_z(WY, y_)) for y_ in yg]
        + [proj(WY, LX, Z_SHALLOW), proj(WY, 0, Z_SHALLOW)]
    )
    ax.add_patch(Polygon(
        pts_wat_fr, closed=True,
        facecolor=PALETTE["water_right"], edgecolor="none", alpha=0.46, zorder=13
    ))

    # -----------------------------------------------------------------------
    # LAYER 4: Free Surface Water Mesh (60 x 120 cells, dx = dy = 50 m)
    # -----------------------------------------------------------------------
    XX, YY = np.meshgrid(xg, yg, indexing="ij")
    ZZ_surf = free_surface_z(XX, YY)

    water_cmap = LinearSegmentedColormap.from_list(
        "tufte_water_bench", ["#7FAAC6", "#B3D2E5", "#E4F1F8"]
    )
    chan_cmap = LinearSegmentedColormap.from_list(
        "tufte_chan_bench", ["#4E82A5", "#76A8C8", "#B3D5E8"]
    )
    z_s_min, z_s_max = ZZ_surf.min(), ZZ_surf.max()

    for i in range(nx_pts - 1):
        for j in range(ny_pts - 1):
            xs = [XX[i, j], XX[i + 1, j], XX[i + 1, j + 1], XX[i, j + 1]]
            ys = [YY[i, j], YY[i + 1, j], YY[i + 1, j + 1], YY[i, j + 1]]
            zs = [ZZ_surf[i, j], ZZ_surf[i + 1, j], ZZ_surf[i + 1, j + 1], ZZ_surf[i, j + 1]]
            X2, Y2 = proj(xs, ys, zs)
            z_mean = 0.25 * sum(zs)
            x_mean = 0.25 * sum(xs)
            norm_z = (z_mean - z_s_min) / (z_s_max - z_s_min + 1e-9)
            dz_dy = (ZZ_surf[i, j + 1] - ZZ_surf[i, j]) / (yg[1] - yg[0])
            light = np.clip(0.60 * norm_z + 0.30 - 0.30 * dz_dy, 0.08, 0.96)
            # Highlight the central deep channel strip on the surface
            in_channel = (XC_L <= x_mean <= XC_R)
            col = chan_cmap(light) if in_channel else water_cmap(light)
            alpha_p = 0.82 if in_channel else 0.72
            ax.add_patch(Polygon(
                list(zip(X2, Y2)),
                facecolor=col, edgecolor=col, lw=0.10, alpha=alpha_p, zorder=15
            ))

    # Fine computational finite-difference grid lines on the free surface (60 x 120 cells)
    for i in range(0, nx_pts, 3):
        ax.plot(*proj(XX[i, :], YY[i, :], ZZ_surf[i, :]),
                color=PALETTE["water_mesh"], lw=0.38, alpha=0.55, zorder=15.5)
    for j in range(0, ny_pts, 3):
        ax.plot(*proj(XX[:, j], YY[:, j], ZZ_surf[:, j]),
                color=PALETTE["water_mesh"], lw=0.38, alpha=0.55, zorder=15.5)

    # Dashed longitudinal surface lines demarcating the submerged deep channel banks
    for x_bank in [XC_L, XC_R]:
        ax.plot(*proj(np.full(ny_pts, x_bank), yg, free_surface_z(x_bank, yg)),
                color=PALETTE["navy_deep"], lw=0.95, ls="--", alpha=0.80, zorder=16)

    # Crisp Foreground Structural Outlines
    ax.plot(*proj(xg, np.zeros(nx_pts), free_surface_z(xg, 0)),
            color=PALETTE["water_edge"], lw=1.45, zorder=17)
    ax.plot(*proj(np.full(ny_pts, WY), yg, free_surface_z(WY, yg)),
            color=PALETTE["water_edge"], lw=1.40, zorder=17)

    # Stepped seabed front edge outline
    stepped_edge_x = [0, XC_L, XC_L, XC_R, XC_R, WY]
    stepped_edge_z = [Z_SHALLOW, Z_SHALLOW, Z_DEEP, Z_DEEP, Z_SHALLOW, Z_SHALLOW]
    ax.plot(*proj(stepped_edge_x, np.zeros(6), stepped_edge_z),
            color=PALETTE["bed_edge"], lw=1.55, zorder=17.5)

    # Vertical corner edges of the block
    for (xc_e, yc_e), lw_e in [((0, 0), 1.20), ((WY, 0), 1.35), ((WY, LX), 1.10)]:
        ax.plot(*proj([xc_e, xc_e], [yc_e, yc_e], [Z_BASE, free_surface_z(xc_e, yc_e)]),
                color=PALETTE["water_edge"], lw=lw_e, zorder=17)

    # Datum z = 0 dashed reference line across the front and right faces
    ax.plot(*proj([0, WY], [0, 0], [0, 0]),
            color=PALETTE["rule_dark"], lw=0.95, ls=(0, (4, 3)), zorder=17.2)
    ax.plot(*proj([WY, WY], [0, LX], [0, 0]),
            color=PALETTE["rule_dark"], lw=0.85, ls=(0, (4, 3)), zorder=17.2)

    # -----------------------------------------------------------------------
    # LAYER 5: Semidiurnal Tide Physics (M_2 Wave Entrance + Spreading Arrows)
    # -----------------------------------------------------------------------
    xc_mid = 0.5 * (XC_L + XC_R)

    # 1. Curved tidal flow arrows advancing up the deep channel and spreading laterally!
    draw_3d_arrow(
        ax, (xc_mid, 0.25, free_surface_z(xc_mid, 0.25) + 0.04),
        (xc_mid, 3.05, free_surface_z(xc_mid, 3.05) + 0.04),
        color=PALETTE["navy_deep"], lw=2.3, mutation_scale=13.5, zorder=22
    )
    draw_3d_arrow(
        ax, (xc_mid, 3.30, free_surface_z(xc_mid, 3.30) + 0.04),
        (xc_mid, 6.50, free_surface_z(xc_mid, 6.50) + 0.04),
        color=PALETTE["navy_deep"], lw=2.0, mutation_scale=12.5, zorder=22
    )
    draw_3d_arrow(
        ax, (xc_mid, 6.75, free_surface_z(xc_mid, 6.75) + 0.04),
        (xc_mid, 9.35, free_surface_z(xc_mid, 9.35) + 0.04),
        color=PALETTE["navy_deep"], lw=1.7, mutation_scale=11.0, zorder=22
    )

    # Lateral spreading curved arrows onto Left Shallow Shelf (x < XC_L) and Right Shallow Shelf (x > XC_R)
    for y_sp, x_dest_L, x_dest_R in [(2.1, 1.05, 6.35), (5.0, 0.95, 6.45), (7.8, 1.15, 6.25)]:
        p0_L = proj(XC_L + 0.08, y_sp, free_surface_z(XC_L, y_sp) + 0.03)
        p1_L = proj(x_dest_L, y_sp + 1.15, free_surface_z(x_dest_L, y_sp + 1.15) + 0.03)
        draw_2d_arrow(ax, p0_L, p1_L, color=PALETTE["z_node"], lw=1.45,
                      mutation_scale=10.0, connectionstyle="arc3,rad=0.22", zorder=21)

        p0_R = proj(XC_R - 0.08, y_sp, free_surface_z(XC_R, y_sp) + 0.03)
        p1_R = proj(x_dest_R, y_sp + 1.15, free_surface_z(x_dest_R, y_sp + 1.15) + 0.03)
        draw_2d_arrow(ax, p0_R, p1_R, color=PALETTE["z_node"], lw=1.45,
                      mutation_scale=10.0, connectionstyle="arc3,rad=-0.22", zorder=21)

    # 2. Sinusoidal Tidal Wave M_2 Oscillating Directly at the Front Channel Entrance (y = 0, x in [XC_L, XC_R])
    #    Oscillates strictly along the upper water level z = 0 at the channel mouth (never crossing the brown soil!)
    x_mouth = np.linspace(XC_L + 0.06, XC_R - 0.06, 80)
    s_mouth = (x_mouth - (XC_L + 0.06)) / ((XC_R - XC_L) - 0.12)
    z_mouth_wave = 0.19 * np.sin(2.0 * np.pi * s_mouth)

    Xw_m, Yw_m = proj(x_mouth, np.zeros_like(x_mouth), z_mouth_wave)
    Xw_m0, Yw_m0 = proj(x_mouth, np.zeros_like(x_mouth), np.zeros_like(x_mouth))
    verts_mouth_wave = list(zip(Xw_m, Yw_m)) + list(zip(Xw_m0[::-1], Yw_m0[::-1]))
    ax.add_patch(Polygon(
        verts_mouth_wave, closed=True,
        facecolor=PALETTE["water_top"], edgecolor="none", alpha=0.75, zorder=19
    ))
    ax.plot(Xw_m, Yw_m, color=PALETTE["terracotta"], lw=2.1, zorder=21)

    # Crest of the entrance sine wave at s_mouth = 0.25
    x_crest_m = (XC_L + 0.06) + 0.25 * ((XC_R - XC_L) - 0.12)
    p_crest_0 = proj(x_crest_m, 0.0, 0.0)
    p_crest_1 = proj(x_crest_m, 0.0, 0.19)
    draw_2d_arrow(ax, p_crest_0, p_crest_1,
                  color=PALETTE["terracotta"], lw=1.25, mutation_scale=7.5, arrowstyle="<|-|>", zorder=23)

    # Clean leader line from the entrance wave crest to the label in the upper-left margin
    p_m2_lbl = (-2.15, 0.88)
    draw_2d_arrow(ax, (p_m2_lbl[0] + 0.05, p_m2_lbl[1] - 0.05),
                  (p_crest_1[0] - 0.04, p_crest_1[1] + 0.02),
                  color=PALETTE["terracotta"], lw=0.95, mutation_scale=8.0,
                  connectionstyle="arc3,rad=0.14", zorder=24)
    crisp_text(
        ax, p_m2_lbl[0], p_m2_lbl[1],
        r"Maré $M_2$ na entrada ($a = 0{,}4\text{ m}$)" + "\n" + r"oscilando em torno de $z = 0$",
        color=PALETTE["terracotta"], stroke_w=0.16, bg_clear=True, pad=0.05,
        fontsize=8.3, fontweight="bold", ha="right", va="center", linespacing=1.15, zorder=25
    )

    # -----------------------------------------------------------------------
    # LAYER 6: Engineering Dimension Arrows & Bathymetry Annotations
    # -----------------------------------------------------------------------
    # 1. Shallow depth h = 0.5 m dimension on Front-Left Shelf (x = 0.55) with clean leader line
    p_sh_top = proj(0.55, 0, 0.0)
    p_sh_bot = proj(0.55, 0, Z_SHALLOW)
    draw_2d_arrow(ax, p_sh_bot, p_sh_top, color=PALETTE["navy_deep"], lw=1.1,
                  mutation_scale=6.5, arrowstyle="<|-|>", zorder=22)
    p_sh_mid = (0.5 * (p_sh_top[0] + p_sh_bot[0]), 0.5 * (p_sh_top[1] + p_sh_bot[1]))
    p_sh_lbl = (p_sh_mid[0] - 0.72, p_sh_mid[1] + 0.04)
    ax.plot([p_sh_lbl[0] + 0.04, p_sh_mid[0] - 0.05], [p_sh_lbl[1], p_sh_mid[1]],
            color=PALETTE["navy_deep"], lw=0.80, ls="-", zorder=22)
    crisp_text(
        ax, p_sh_lbl[0], p_sh_lbl[1],
        r"Bacia rasa: $h = 0{,}5\text{ m}$",
        color=PALETTE["navy_deep"], stroke_w=0.16, bg_clear=True, pad=0.04,
        fontsize=8.3, fontweight="bold", ha="right", va="center", zorder=25
    )

    # 2. Deep channel depth h = 5 m dimension inside the central cut (x = XC_R - 0.24)
    x_ch_dim = XC_R - 0.24
    p_ch_top = proj(x_ch_dim, 0, 0.0)
    p_ch_bot = proj(x_ch_dim, 0, Z_DEEP)
    draw_2d_arrow(ax, p_ch_bot, p_ch_top, color="#FFFFFF", lw=1.35,
                  mutation_scale=8.0, arrowstyle="<|-|>", zorder=23)
    draw_2d_arrow(ax, p_ch_bot, p_ch_top, color=PALETTE["navy_deep"], lw=1.15,
                  mutation_scale=7.5, arrowstyle="<|-|>", zorder=24)
    crisp_text(
        ax, proj(XC_R + 0.18, 0, 0.55 * Z_DEEP)[0],
        proj(XC_R + 0.18, 0, 0.55 * Z_DEEP)[1],
        r"Canal profundo: $h = 5\text{ m}$",
        color=PALETTE["navy_deep"], stroke_w=0.17, bg_color=PALETTE["bed_front"], pad=0.05,
        fontsize=8.3, fontweight="bold", ha="left", va="center", zorder=25
    )

    # 3. Channel width dimension: 300 m (with comfortable vertical breathing room below the arrow!)
    p_cw_L = proj(XC_L, 0, Z_DEEP - 0.22)
    p_cw_R = proj(XC_R, 0, Z_DEEP - 0.22)
    ax.plot(*proj([XC_L, XC_L], [0, 0], [Z_DEEP, Z_DEEP - 0.30]),
            color=PALETTE["ink_primary"], lw=0.70, ls=":", zorder=19)
    ax.plot(*proj([XC_R, XC_R], [0, 0], [Z_DEEP, Z_DEEP - 0.30]),
            color=PALETTE["ink_primary"], lw=0.70, ls=":", zorder=19)
    draw_2d_arrow(ax, p_cw_L, p_cw_R, color=PALETTE["ink_primary"], lw=1.15,
                  mutation_scale=8.0, arrowstyle="<|-|>", zorder=22)
    crisp_text(
        ax, 0.5 * (p_cw_L[0] + p_cw_R[0]), 0.5 * (p_cw_L[1] + p_cw_R[1]) - 0.22,
        r"Largura do canal: $300\text{ m}$",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_color=PALETTE["bed_front"], pad=0.03,
        fontsize=8.1, fontweight="bold", ha="center", va="top", zorder=25
    )

    # 4. Total Basin Width dimension: 3000 m (outside front-left base)
    z_dim_w = Z_BASE - 0.32
    p_bw_0 = proj(0, 0, z_dim_w)
    p_bw_1 = proj(WY, 0, z_dim_w)
    ax.plot(*proj([0, 0], [0, 0], [Z_BASE, z_dim_w - 0.08]),
            color=PALETTE["ink_muted"], lw=0.70, ls=":", zorder=15)
    ax.plot(*proj([WY, WY], [0, 0], [Z_BASE, z_dim_w - 0.08]),
            color=PALETTE["ink_muted"], lw=0.70, ls=":", zorder=15)
    draw_2d_arrow(ax, p_bw_0, p_bw_1, color=PALETTE["ink_primary"], lw=1.15,
                  mutation_scale=8.5, arrowstyle="<|-|>", zorder=20)
    crisp_text(
        ax, 0.5 * (p_bw_0[0] + p_bw_1[0]) - 0.25, 0.5 * (p_bw_0[1] + p_bw_1[1]) - 0.14,
        r"Largura da bacia: $3000\text{ m}$ ($60\text{ células},\; \Delta y = 50\text{ m}$)",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_clear=True, pad=0.04,
        fontsize=8.4, fontweight="bold", ha="center", va="top", zorder=25
    )

    # 5. Total Basin Length dimension: 6000 m (outside front-right base)
    p_bl_0 = proj(WY, 0, z_dim_w)
    p_bl_1 = proj(WY, LX, z_dim_w)
    ax.plot(*proj([WY, WY], [LX, LX], [Z_BASE, z_dim_w - 0.08]),
            color=PALETTE["ink_muted"], lw=0.70, ls=":", zorder=15)
    draw_2d_arrow(ax, p_bl_0, p_bl_1, color=PALETTE["ink_primary"], lw=1.15,
                  mutation_scale=8.5, arrowstyle="<|-|>", zorder=20)
    crisp_text(
        ax, 0.5 * (p_bl_0[0] + p_bl_1[0]) + 0.20, 0.5 * (p_bl_0[1] + p_bl_1[1]) - 0.14,
        r"Comprimento da bacia: $6000\text{ m}$ ($120\text{ células},\; \Delta x = 50\text{ m}$)",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_clear=True, pad=0.04,
        fontsize=8.4, fontweight="bold", ha="left", va="top", zorder=25
    )

    # 6. Surface Mesh Callout Badge placed cleanly on the upper-right of the water surface
    p_mesh_target = proj(5.60, 5.20, free_surface_z(5.60, 5.20))
    p_mesh_lbl = (p_mesh_target[0] + 1.15, p_mesh_target[1] - 0.72)
    ax.plot(*p_mesh_target, marker="o", markersize=3.8, color=PALETTE["navy_deep"], zorder=25)
    draw_2d_arrow(ax, (p_mesh_lbl[0] - 0.12, p_mesh_lbl[1] + 0.15), p_mesh_target,
                  color=PALETTE["navy_deep"], lw=0.90, mutation_scale=8.0,
                  connectionstyle="arc3,rad=-0.15", zorder=24)
    crisp_text(
        ax, p_mesh_lbl[0], p_mesh_lbl[1],
        r"Malha $60 \times 120$ células" + "\n"
        + r"($\Delta x = \Delta y = 50\text{ m}$, $N = 7200$)",
        color=PALETTE["navy_deep"], stroke_w=0.16, bg_clear=True, pad=0.06,
        fontsize=8.3, fontweight="bold", ha="left", va="center", linespacing=1.18, zorder=26
    )

    # 7. Closed Margin Callout Labels (u_n = 0) on the back-left and back-right edges
    p_marg_L = proj(0, 4.8, 0.14)
    crisp_text(
        ax, p_marg_L[0] - 0.25, p_marg_L[1] + 0.15,
        r"Margem fechada ($u_n = 0$)",
        color=PALETTE["bed_edge"], stroke_w=0.15, bg_clear=True, pad=0.04,
        fontsize=8.2, fontweight="bold", fontstyle="italic", ha="right", va="bottom", zorder=25
    )
    p_marg_B = proj(3.7, LX, 0.16)
    crisp_text(
        ax, p_marg_B[0] - 0.20, p_marg_B[1] + 0.20,
        r"Cabeceira fechada ($u_n = 0$)",
        color=PALETTE["bed_edge"], stroke_w=0.15, bg_clear=True, pad=0.04,
        fontsize=8.2, fontweight="bold", fontstyle="italic", ha="center", va="bottom", zorder=25
    )

    # 8. Datum label z = 0 placed cleanly outside the front-right water corner with a dashed extension line
    p_dat_R = proj(WY, 0.65, 0.0)
    p_dat_lbl = (p_dat_R[0] + 0.95, p_dat_R[1] - 0.22)
    ax.plot(*proj([WY, WY], [0, 0.65], [0.0, 0.0]),
            color=PALETTE["rule_dark"], lw=1.0, ls=(0, (4, 3)), zorder=22)
    ax.plot(p_dat_R[0], p_dat_R[1], marker="o", markersize=3.4, color=PALETTE["rule_dark"], zorder=24)
    ax.plot([p_dat_R[0], p_dat_lbl[0] - 0.06], [p_dat_R[1], p_dat_lbl[1]],
            color=PALETTE["rule_dark"], lw=0.90, ls="--", zorder=23)
    crisp_text(
        ax, p_dat_lbl[0], p_dat_lbl[1],
        r"Nível médio $z = 0$",
        color=PALETTE["rule_dark"], stroke_w=0.15, bg_clear=True, pad=0.04,
        fontsize=8.1, fontweight="bold", fontstyle="italic", ha="left", va="center", zorder=25
    )

    # -----------------------------------------------------------------------
    # LAYER 7: 12-Hour Celestial Solar Arc Above the Expanded 3D Basin
    # -----------------------------------------------------------------------
    x_sun_L, y_sun_L = -4.55, 2.35
    x_sun_M, y_sun_M = 1.65, 4.95
    x_sun_R, y_sun_R = 7.85, 3.05

    s_arc = np.linspace(0, 1, 120)
    P0_sun = np.array([x_sun_L, y_sun_L])
    P2_sun = np.array([x_sun_R, y_sun_R])
    P_mid_sun = np.array([x_sun_M, y_sun_M])
    P1_sun = 2.0 * P_mid_sun - 0.5 * (P0_sun + P2_sun)

    arc_pts = (
        ((1 - s_arc) ** 2)[:, None] * P0_sun
        + (2 * (1 - s_arc) * s_arc)[:, None] * P1_sun
        + (s_arc ** 2)[:, None] * P2_sun
    )
    ax.plot(arc_pts[:, 0], arc_pts[:, 1],
            color=PALETTE["amber_sun"], lw=1.45, ls=(0, (5, 3)), alpha=0.88, zorder=19)

    for s_arr in [0.26, 0.74]:
        pt_a = (1 - s_arr) ** 2 * P0_sun + 2 * (1 - s_arr) * s_arr * P1_sun + (s_arr ** 2) * P2_sun
        s_nxt = s_arr + 0.02
        pt_b = (1 - s_nxt) ** 2 * P0_sun + 2 * (1 - s_nxt) * s_nxt * P1_sun + (s_nxt ** 2) * P2_sun
        draw_2d_arrow(ax, tuple(pt_a), tuple(pt_b),
                      color=PALETTE["amber_sun"], lw=1.4, mutation_scale=9.5, zorder=20)

    # 3 Stylized Minimalist Suns: Nascente (t = 0 h), Zênite (t = 6 h), Poente (t = 12 h)
    draw_stylized_sun(ax, x_sun_L, y_sun_L, color=PALETTE["amber_sun"], zorder=25)
    crisp_text(
        ax, x_sun_L, y_sun_L - 0.34,
        r"$t = 0\text{ h}$" + "\n(Nascente)",
        color=PALETTE["amber_sun"], stroke_w=0.16, bg_clear=True, pad=0.03,
        fontsize=8.2, fontweight="bold", ha="center", va="top", linespacing=1.12, zorder=26
    )

    draw_stylized_sun(ax, x_sun_M, y_sun_M, color=PALETTE["amber_sun"], zorder=25)
    crisp_text(
        ax, x_sun_M, y_sun_M + 0.34,
        r"$t = 6\text{ h}$ (Zênite)",
        color=PALETTE["amber_sun"], stroke_w=0.17, bg_clear=True, pad=0.04,
        fontsize=8.4, fontweight="bold", ha="center", va="bottom", zorder=26
    )

    draw_stylized_sun(ax, x_sun_R, y_sun_R, color=PALETTE["amber_sun"], zorder=25)
    crisp_text(
        ax, x_sun_R + 0.34, y_sun_R,
        r"$t = 12\text{ h}$" + "\n(Poente)",
        color=PALETTE["amber_sun"], stroke_w=0.16, bg_clear=True, pad=0.03,
        fontsize=8.2, fontweight="bold", ha="left", va="center", linespacing=1.12, zorder=26
    )

    # Discrete label along the celestial arc
    crisp_text(
        ax, x_sun_M, y_sun_M - 0.40,
        r"Ciclo semidiurno $M_2$: $T = 12\text{ h}$ ($720$ passos de $\Delta t = 60\text{ s}$)",
        color=PALETTE["amber_sun"], stroke_w=0.16, bg_clear=True, pad=0.06,
        fontsize=8.6, fontweight="bold", fontstyle="italic", ha="center", va="top", zorder=26
    )

    # =======================================================================
    # 2. BOTTOM QUANTITATIVE SYNTHESIS STRIP (4 COMPACT MONOGRAPH CARDS)
    # =======================================================================
    y_sep = -3.35
    ax.plot([-5.55, 8.85], [y_sep, y_sep], color=PALETTE["rule_dark"], lw=1.10, zorder=15)
    ax.plot([-5.55, 8.85], [y_sep - 0.06, y_sep - 0.06], color=PALETTE["rule_dark"], lw=0.50, zorder=15)

    card_w = 3.42
    card_h = 2.02
    card_y = -5.55
    card_gap = 0.22
    x_starts = [-5.55 + k * (card_w + card_gap) for k in range(4)]

    # -----------------------------------------------------------------------
    # CARD 1 (Navy Blue): "Quebra CFL (Canal h = 5 m)"
    # -----------------------------------------------------------------------
    x1 = x_starts[0]
    draw_drafting_frame(ax, x1, card_y, card_w, card_h,
                        ec=PALETTE["navy_deep"], fc=PALETTE["card_bg"], lw=1.05, double_top=True, zorder=5)
    crisp_text(
        ax, x1 + 0.5 * card_w, card_y + card_h - 0.14,
        r"1. Quebra CFL (Canal $h = 5\text{ m}$)",
        color=PALETTE["navy_deep"], stroke_w=0.18,
        fontsize=8.6, fontweight="bold", ha="center", va="top", zorder=20
    )
    ax.plot([x1 + 0.14, x1 + card_w - 0.14], [card_y + card_h - 0.42, card_y + card_h - 0.42],
            color=PALETTE["rule_light"], lw=0.65, zorder=10)

    # Mini Horizontal Bar Comparison: Explícito (C_r <= 1) vs. Casulli (C_r = 8)
    bx0_1 = x1 + 0.92
    bw_max_1 = 1.95
    # Bar A: Explícito (1/8 of max width)
    y_b1_a = card_y + 1.18
    ax.add_patch(Rectangle(
        (bx0_1, y_b1_a - 0.11), bw_max_1 * (1.0 / 8.0), 0.22,
        facecolor=PALETTE["ink_muted"], edgecolor=PALETTE["ink_primary"], lw=0.75, zorder=15
    ))
    crisp_text(ax, bx0_1 - 0.08, y_b1_a, "Explícito:",
               color=PALETTE["ink_secondary"], stroke_w=0.14,
               fontsize=7.8, fontweight="bold", ha="right", va="center", zorder=20)
    crisp_text(ax, bx0_1 + bw_max_1 * (1.0 / 8.0) + 0.10, y_b1_a, r"$C_r \leq 1$ (limite rígido)",
               color=PALETTE["ink_secondary"], stroke_w=0.13,
               fontsize=7.7, ha="left", va="center", zorder=20)

    # Bar B: Casulli (8/8 full width)
    y_b1_b = card_y + 0.72
    ax.add_patch(Rectangle(
        (bx0_1, y_b1_b - 0.12), bw_max_1, 0.24,
        facecolor=PALETTE["navy_deep"], edgecolor=PALETTE["ink_primary"], lw=0.80, zorder=15
    ))
    crisp_text(ax, bx0_1 - 0.08, y_b1_b, "Casulli:",
               color=PALETTE["navy_deep"], stroke_w=0.16,
               fontsize=7.9, fontweight="bold", ha="right", va="center", zorder=20)
    crisp_text(ax, bx0_1 + 0.5 * bw_max_1, y_b1_b, r"$C_r = 8$ ($\Delta t = 60\text{ s}$)",
               color="#FFFFFF", stroke_w=0.16,
               fontsize=7.7, fontweight="bold", ha="center", va="center", zorder=22)

    crisp_text(
        ax, x1 + 0.5 * card_w, card_y + 0.24,
        r"Passo $\geq 8\times$ maior que o limite explícito",
        color=PALETTE["navy_deep"], stroke_w=0.15,
        fontsize=7.9, fontweight="bold", fontstyle="italic", ha="center", va="center", zorder=20
    )

    # -----------------------------------------------------------------------
    # CARD 2 (Sea-Teal): "CPU CRAY X-MP/48 (1 ciclo)"
    # -----------------------------------------------------------------------
    x2 = x_starts[1]
    draw_drafting_frame(ax, x2, card_y, card_w, card_h,
                        ec=PALETTE["teal_adi"], fc=PALETTE["card_bg"], lw=1.05, double_top=True, zorder=5)
    crisp_text(
        ax, x2 + 0.5 * card_w, card_y + card_h - 0.14,
        r"2. CPU CRAY X-MP/48 ($1\text{ ciclo}$)",
        color=PALETTE["teal_adi"], stroke_w=0.18,
        fontsize=8.6, fontweight="bold", ha="center", va="top", zorder=20
    )
    ax.plot([x2 + 0.14, x2 + card_w - 0.14], [card_y + card_h - 0.42, card_y + card_h - 0.42],
            color=PALETTE["rule_light"], lw=0.65, zorder=10)

    # Proportional Horizontal Bars: Pentadiagonal (79 s) vs. ADI (32 s)
    bx0_2 = x2 + 1.12
    bw_max_2 = 1.75
    # Bar A: Pentadiagonal 79 s
    y_b2_a = card_y + 1.18
    ax.add_patch(Rectangle(
        (bx0_2, y_b2_a - 0.11), bw_max_2, 0.22,
        facecolor=PALETTE["water_right"], edgecolor=PALETTE["navy_deep"], lw=0.75, zorder=15
    ))
    crisp_text(ax, bx0_2 - 0.08, y_b2_a, "Pentadiag.:",
               color=PALETTE["ink_secondary"], stroke_w=0.14,
               fontsize=7.8, fontweight="bold", ha="right", va="center", zorder=20)
    crisp_text(ax, bx0_2 + bw_max_2 + 0.08, y_b2_a, r"$79\text{ s}$",
               color=PALETTE["ink_primary"], stroke_w=0.16,
               fontsize=7.9, fontweight="bold", ha="left", va="center", zorder=20)

    # Bar B: ADI 32 s (32 / 79 of max width)
    y_b2_b = card_y + 0.72
    bw_adi = bw_max_2 * (32.0 / 79.0)
    ax.add_patch(Rectangle(
        (bx0_2, y_b2_b - 0.12), bw_adi, 0.24,
        facecolor=PALETTE["teal_adi"], edgecolor=PALETTE["ink_primary"], lw=0.80, zorder=15
    ))
    crisp_text(ax, bx0_2 - 0.08, y_b2_b, "ADI (Thomas):",
               color=PALETTE["teal_adi"], stroke_w=0.16,
               fontsize=7.8, fontweight="bold", ha="right", va="center", zorder=20)
    crisp_text(ax, bx0_2 + bw_adi + 0.08, y_b2_b, r"$32\text{ s}$ ($-60\%$ tempo)",
               color=PALETTE["teal_adi"], stroke_w=0.16,
               fontsize=7.9, fontweight="bold", ha="left", va="center", zorder=20)

    crisp_text(
        ax, x2 + 0.5 * card_w, card_y + 0.24,
        r"$99\%$ concordância em $\Delta t = 60\text{ s}$",
        color=PALETTE["teal_adi"], stroke_w=0.15,
        fontsize=7.9, fontweight="bold", fontstyle="italic", ha="center", va="center", zorder=20
    )

    # -----------------------------------------------------------------------
    # CARD 3 (Slate Blue): "Massa & Regime Permanente"
    # -----------------------------------------------------------------------
    x3 = x_starts[2]
    draw_drafting_frame(ax, x3, card_y, card_w, card_h,
                        ec=PALETTE["slate_blue"], fc=PALETTE["card_bg"], lw=1.05, double_top=True, zorder=5)
    crisp_text(
        ax, x3 + 0.5 * card_w, card_y + card_h - 0.14,
        r"3. Massa & Regime Permanente",
        color=PALETTE["slate_blue"], stroke_w=0.18,
        fontsize=8.6, fontweight="bold", ha="center", va="top", zorder=20
    )
    ax.plot([x3 + 0.14, x3 + card_w - 0.14], [card_y + card_h - 0.42, card_y + card_h - 0.42],
            color=PALETTE["rule_light"], lw=0.65, zorder=10)

    # Mini plot of 2 identical overlapping curves: t = 108 h (9º ciclo) vs t = 120 h (10º ciclo)
    px0_3, py0_3, pw_3, ph_3 = x3 + 0.25, card_y + 0.58, 1.45, 0.85
    ax.add_patch(Rectangle(
        (px0_3, py0_3), pw_3, ph_3,
        facecolor="#FFFFFF", edgecolor=PALETTE["ink_muted"], lw=0.75, zorder=14
    ))
    ax.plot([px0_3 + 0.06, px0_3 + pw_3 - 0.06], [py0_3 + 0.5 * ph_3, py0_3 + 0.5 * ph_3],
            color=PALETTE["rule_light"], lw=0.55, ls=":", zorder=15)
    ts_3 = np.linspace(0, 2 * np.pi, 70)
    xs_3 = px0_3 + 0.08 + (ts_3 / (2 * np.pi)) * (pw_3 - 0.16)
    ys_3 = py0_3 + 0.5 * ph_3 + 0.30 * ph_3 * np.sin(ts_3)
    # Curve 1: t = 108 h (solid light cerulean)
    ax.plot(xs_3, ys_3, color=PALETTE["water_channel"], lw=2.4, alpha=0.80, zorder=16)
    # Curve 2: t = 120 h (dashed deep navy directly on top!)
    ax.plot(xs_3, ys_3, color=PALETTE["navy_deep"], lw=1.35, ls="--", zorder=17)

    crisp_text(
        ax, px0_3 + pw_3 + 0.12, card_y + 1.18,
        r"— Ciclo 9 ($108\text{ h}$)" + "\n" + r"-- Ciclo 10 ($120\text{ h}$)",
        color=PALETTE["slate_blue"], stroke_w=0.15,
        fontsize=7.7, fontweight="bold", ha="left", va="center", linespacing=1.25, zorder=20
    )
    crisp_text(
        ax, px0_3 + pw_3 + 0.12, card_y + 0.72,
        r"$t = 108\text{ h} \approx t = 120\text{ h}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=7.7, fontweight="bold", ha="left", va="center", zorder=20
    )

    crisp_text(
        ax, x3 + 0.5 * card_w, card_y + 0.24,
        r"$4$ casas decimais | massa conservada",
        color=PALETTE["slate_blue"], stroke_w=0.15,
        fontsize=7.9, fontweight="bold", fontstyle="italic", ha="center", va="center", zorder=20
    )

    # -----------------------------------------------------------------------
    # CARD 4 (Terracotta — Caution): "Limite do ADI"
    # -----------------------------------------------------------------------
    x4 = x_starts[3]
    draw_drafting_frame(ax, x4, card_y, card_w, card_h,
                        ec=PALETTE["terracotta"], fc="#FAF2EE", lw=1.10, double_top=True, zorder=5)
    crisp_text(
        ax, x4 + 0.5 * card_w, card_y + card_h - 0.14,
        r"4. Limite do ADI (Cautela em $\Delta t$)",
        color=PALETTE["terracotta"], stroke_w=0.18,
        fontsize=8.6, fontweight="bold", ha="center", va="top", zorder=20
    )
    ax.plot([x4 + 0.14, x4 + card_w - 0.14], [card_y + card_h - 0.42, card_y + card_h - 0.42],
            color=PALETTE["rule_light"], lw=0.65, zorder=10)

    # Discrete Warning Triangle Icon (!) on the left of Card 4
    tx_w, ty_w = x4 + 0.55, card_y + 1.00
    tri_warn = [
        (tx_w - 0.28, ty_w - 0.24),
        (tx_w + 0.28, ty_w - 0.24),
        (tx_w, ty_w + 0.28),
    ]
    ax.add_patch(Polygon(
        tri_warn, closed=True,
        facecolor="#F9E0D8", edgecolor=PALETTE["terracotta"], lw=1.25, zorder=16
    ))
    crisp_text(ax, tx_w, ty_w - 0.06, "!",
               color=PALETTE["terracotta"], stroke_w=0.22,
               fontsize=11.0, fontweight="bold", ha="center", va="center", zorder=18)

    crisp_text(
        ax, x4 + 1.02, card_y + 1.18,
        r"Passo extremo: $\Delta t = 360\text{ s}$",
        color=PALETTE["terracotta"], stroke_w=0.17,
        fontsize=8.1, fontweight="bold", ha="left", va="center", zorder=20
    )
    crisp_text(
        ax, x4 + 1.02, card_y + 0.78,
        r"Erro direcional até $10\%$ vs. 2D" + "\n"
        + r"(quebra de simetria do splitting)",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=7.7, ha="left", va="center", linespacing=1.20, zorder=20
    )

    crisp_text(
        ax, x4 + 0.5 * card_w, card_y + 0.24,
        r"Para $\Delta t$ extremo, preferir o esquema 2D acoplado",
        color=PALETTE["terracotta"], stroke_w=0.15,
        fontsize=7.9, fontweight="bold", fontstyle="italic", ha="center", va="center", zorder=20
    )

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-5.80, 9.10)
    ax.set_ylim(-5.75, 5.35)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.12)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_casulli_benchmark.svg"
    pdf_path = out_dir / "swe_casulli_benchmark.pdf"
    png_path = out_dir / "swe_casulli_benchmark.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
