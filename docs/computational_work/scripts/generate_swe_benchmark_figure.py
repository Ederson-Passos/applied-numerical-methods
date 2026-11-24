"""
Generate an authentic 1980s/1990s Coastal Engineering / Journal of Computational
Physics (Casulli 1990) vector scientific illustration of the Semidiurnal M_2
Tidal Cycle in a Shallow Basin with a Deep Central Navigation Channel, showing
the TWO EXTREME HYDRODYNAMIC STATES STACKED VERTICALLY (one above the other):

  - TOP PANEL (Estágio A — Enchente / Preamar, z = +0,4 m):
      * Tidal piston pushes water rapidly up the deep central channel (low friction,
        high celerity c = sqrt(gH), H = 5,4 m) and overflows laterally onto the
        shallow tidal flats, raising total water depth on the shelves to
        H = 0,5 m + 0,4 m = 0,9 m.
      * Shows the 12h M_2 harmonic tidal curve at the entrance peaking at +0,4 m
        and the celestial cycle (T = 12 h, 720 steps of dt = 60 s).

  - BOTTOM PANEL (Estágio B — Vazante / Baixa-mar, z = -0,4 m):
      * Tidal piston pulls water out; lateral flats drain back into the central
        channel (H = 4,6 m) and out the open mouth.
      * On the lateral tidal flats, water depth drops to a thin 10 cm film:
        H = 0,5 m - 0,4 m = 0,1 m, where bottom friction (-gamma u) dominates
        and local intertidal patches near the margins approach drying (molhamento
        e secagem), testing numerical stability without spurious oscillations.
      * Full engineering dimensions of the basin (3000 m x 6000 m, channel 300 m,
        60 x 120 grid, dx = dy = 50 m) cleanly displayed below the bottom block.

Preserves 100% of Figure 1's editorial art style, warm archival paper (#FAF8F3),
hatched sand-beige seabed, translucent ice-blue water, and razor-sharp LaTeX
Latin Modern Roman & Computer Modern Math typography.

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
#    (Strictly identical to Figure 1 & previous figures!)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FAF8F3",       # Warm cream/ivory archival paper
    "ink_primary": "#11161C",     # Deep obsidian/graphite ink for titles & math
    "ink_secondary": "#222B35",   # Crisp dark charcoal for labels
    "ink_muted": "#626E7A",       # Slate gray for dimension lines & subtle notes
    "rule_dark": "#283648",       # Classic booktabs heavy rule & z = 0 datum
    "rule_light": "#C8BBAE",      # Subtle archival divider rule
    "navy_deep": "#0D3149",       # Deep Prussian navy (titles, deep channel, vectors)
    "z_node": "#145374",          # Cerulean navy
    "water_front": "#A9CCE0",     # Front-left water column face (from Fig 1)
    "water_right": "#8EB8D1",     # Front-right water column face (from Fig 1)
    "water_top": "#D6EAF5",       # Translucent ice-blue water surface
    "water_channel": "#5B92B5",   # Deeper water tint over the central 5 m channel
    "water_film": "#DCEBF3",      # Ultra-thin 10 cm water film tint at low tide
    "sand_wet": "#D6C9B8",        # Exposed/intertidal wet sand bank near drying
    "water_edge": "#204B69",      # Crisp structural water edge
    "water_mesh": "#4A7C9B",      # Fine wave mesh lines
    "bed_top": "#DFD5C7",         # Shallow flat seabed surface (h = 0.5 m)
    "bed_chan_top": "#9E8D7B",    # Deep channel seabed bottom (h = 5.0 m)
    "bed_chan_wall": "#B5A695",   # Vertical side wall of deep channel
    "bed_front": "#C8BBAE",       # Geological cross-section front face (from Fig 1)
    "bed_right": "#B3A494",       # Geological cross-section right face (from Fig 1)
    "bed_edge": "#5E4F41",        # Seabed contour & outline
    "bed_hatch": "#827161",       # Fine geological sediment hatching (from Fig 1)
    "teal_adi": "#17575A",        # Sea-teal for drainage/lateral return vectors
    "terracotta": "#8E321E",      # Venetian terracotta for bottom friction / thin film alert
    "amber_sun": "#A86518",       # Soft warm amber for 12h M_2 celestial/tidal cycle
}


def crisp_text(ax, x, y, s, color="#11161C", stroke_w=0.16, bg_clear=False, bg_color=None, pad=0.06, **kwargs):
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


def draw_stylized_sun(ax, cx, cy, r_core=0.11, r_in=0.15, r_out=0.24, color="#A86518", zorder=25):
    """Draw a classic 1980s astronomical/coastal-engineering vector sun/moon cycle icon."""
    ax.add_patch(Circle(
        (cx, cy), r_core,
        facecolor="#FDF6E7", edgecolor=color, linewidth=1.15, zorder=zorder
    ))
    for k in range(12):
        ang = k * (2.0 * np.pi / 12.0)
        r_tip = r_out if k % 2 == 0 else 0.5 * (r_in + r_out)
        ax.plot(
            [cx + r_in * np.cos(ang), cx + r_tip * np.cos(ang)],
            [cy + r_in * np.sin(ang), cy + r_tip * np.sin(ang)],
            color=color, lw=0.85, zorder=zorder - 1
        )


# ---------------------------------------------------------------------------
# 3. 3D Axonometric Projection & Basin Geometry (Shared by Both States!)
#    - Calibrated so that:
#        h_shallow = 0.5 m -> Z_SHALLOW = -0.35
#        z_high    = +0.4 m -> +0.28  (Total shelf depth H = 0.63 -> 0.9 m!)
#        z_low     = -0.4 m -> -0.28  (Total shelf depth H = 0.07 -> 0.1 m = 10 cm film!)
#        h_deep    = 5.0 m -> Z_DEEP = -0.92, with channel width = 1.84 (2:1 wider than deep!)
# ---------------------------------------------------------------------------
WY = 7.20         # Basin width 3000 m
LX = 9.40         # Basin length 6000 m
XC_L = 2.68       # Deep channel left bank
XC_R = 4.52       # Deep channel right bank (width = 1.84 >> depth 0.92!)

Z_DATUM = 0.00    # Undisturbed reference level z = 0
Z_SHALLOW = -0.35 # Shallow tidal flat bed z = -0.5 m
Z_DEEP = -0.92    # Deep central channel bed z = -5.0 m
Z_BASE = -1.42    # Geological block base

angle_x = np.deg2rad(-14.5)
angle_y = np.deg2rad(24.0)
scale_x = 0.96
scale_y = 0.62
scale_z = 1.00

EX = np.array([scale_x * np.cos(angle_x), scale_x * np.sin(angle_x)])
EY = np.array([scale_y * np.cos(angle_y), scale_y * np.sin(angle_y)])
EZ = np.array([0.0, scale_z])


def proj_at(x, y, z, orig):
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    z_arr = np.asarray(z)
    X = orig[0] + x_arr * EX[0] + y_arr * EY[0] + z_arr * EZ[0]
    Y = orig[1] + x_arr * EX[1] + y_arr * EY[1] + z_arr * EZ[1]
    return X, Y


def draw_3d_arrow_at(
    ax, p_start, p_end, orig, color, lw=1.35, mutation_scale=11.5,
    arrowstyle="-|>", zorder=20, ls="-", alpha=1.0
):
    x0, y0 = proj_at(*p_start, orig)
    x1, y1 = proj_at(*p_end, orig)
    return draw_2d_arrow(
        ax, (x0, y0), (x1, y1), color=color, lw=lw,
        mutation_scale=mutation_scale, arrowstyle=arrowstyle,
        zorder=zorder, ls=ls, alpha=alpha
    )


def z_surf_high_tide(x, y):
    """
    HIGH TIDE (Preamar / Enchente: z_mouth = +0.4 m => +0.28 canvas units):
    Water enters at +0.28 through the open mouth and forms a gentle advancing
    flood wave cresting along the channel and spreading onto the shallow flats
    (raising H on the flats to ~0.9 m = 0.63 canvas units).
    """
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    xc_mid = 0.5 * (XC_L + XC_R)
    r_lat = np.abs(x_arr - xc_mid) / (0.5 * WY)
    # Flood wave slightly higher in the channel and gently sloping toward margins
    wave = 0.28 - 0.045 * (y_arr / LX) - 0.035 * (r_lat ** 1.4)
    undul = 0.038 * np.cos(2.4 * np.pi * (y_arr / LX) + 0.9 * np.pi * r_lat)
    return wave + undul


def z_surf_low_tide(x, y):
    """
    LOW TIDE (Baixa-mar / Vazante: z_mouth = -0.4 m => -0.28 canvas units):
    Water recedes out the channel mouth at -0.28. On the shallow shelves
    (Z_SHALLOW = -0.35), the surface drops to z approx -0.28 (leaving only a
    10 cm = 0.07 unit thin film!), and near the outer back corners rises
    slightly more slowly due to strong bottom friction, while locally touching
    Z_SHALLOW (wetting/drying limit) near the outer front/mid margins.
    """
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    xc_mid = 0.5 * (XC_L + XC_R)
    r_lat = np.abs(x_arr - xc_mid) / (0.5 * WY)
    # Channel draws down fastest (-0.29), shelves lag slightly into a thin film (-0.27 to -0.33)
    drawdown = -0.285 - 0.035 * np.sin(np.pi * (y_arr / LX)) * (r_lat ** 1.5) + 0.025 * (y_arr / LX)
    undul = 0.018 * np.cos(2.6 * np.pi * (y_arr / LX) - 1.1 * np.pi * r_lat)
    # Clamp just above or at Z_SHALLOW + 0.015 so thin film is visible everywhere, with dry sand patches highlighted
    return np.maximum(Z_SHALLOW + 0.022, drawdown + undul)


def draw_basin_state(ax, orig, mode="high"):
    """
    Render the complete 3D Isometric Cutaway Basin at `orig` for either:
      - mode == "high": Flood / High Tide (+0.4 m, H_shelf = 0.9 m, fast inflow & overflow)
      - mode == "low" : Ebb / Low Tide (-0.4 m, H_shelf = 0.1 m = 10 cm film, friction & drying)
    """
    z_fn = z_surf_high_tide if mode == "high" else z_surf_low_tide
    nx_pts, ny_pts = 56, 72
    xg = np.linspace(0, WY, nx_pts)
    yg = np.linspace(0, LX, ny_pts)
    xc_mid = 0.5 * (XC_L + XC_R)

    # -----------------------------------------------------------------------
    # 1. Submerged Bathymetry Surfaces (Shallow Shelves & Deep Channel)
    # -----------------------------------------------------------------------
    for (xa, xb) in [(0, XC_L), (XC_R, WY)]:
        pts_sh = [
            proj_at(xa, 0, Z_SHALLOW, orig), proj_at(xb, 0, Z_SHALLOW, orig),
            proj_at(xb, LX, Z_SHALLOW, orig), proj_at(xa, LX, Z_SHALLOW, orig),
        ]
        ax.add_patch(Polygon(
            pts_sh, closed=True,
            facecolor=PALETTE["bed_top"], edgecolor=PALETTE["bed_edge"],
            lw=0.75, alpha=0.94, zorder=3
        ))

    # Inner vertical wall of deep channel (x = XC_L)
    pts_wall_L = [
        proj_at(XC_L, 0, Z_DEEP, orig), proj_at(XC_L, LX, Z_DEEP, orig),
        proj_at(XC_L, LX, Z_SHALLOW, orig), proj_at(XC_L, 0, Z_SHALLOW, orig),
    ]
    ax.add_patch(Polygon(
        pts_wall_L, closed=True,
        facecolor=PALETTE["bed_chan_wall"], edgecolor=PALETTE["bed_edge"],
        lw=0.75, alpha=0.95, zorder=3.5
    ))

    # Deep channel floor (x in [XC_L, XC_R])
    pts_ch_bot = [
        proj_at(XC_L, 0, Z_DEEP, orig), proj_at(XC_R, 0, Z_DEEP, orig),
        proj_at(XC_R, LX, Z_DEEP, orig), proj_at(XC_L, LX, Z_DEEP, orig),
    ]
    ax.add_patch(Polygon(
        pts_ch_bot, closed=True,
        facecolor=PALETTE["bed_chan_top"], edgecolor=PALETTE["bed_edge"],
        lw=0.80, alpha=0.95, zorder=3.8
    ))

    # Back walls & closed margin ticks (u_n = 0)
    ax.plot(*proj_at(np.zeros(ny_pts), yg, z_fn(0, yg), orig),
            color=PALETTE["water_edge"], lw=0.80, alpha=0.55, zorder=5)
    ax.plot(*proj_at(xg, np.full(nx_pts, LX), z_fn(xg, LX), orig),
            color=PALETTE["water_edge"], lw=0.80, alpha=0.55, zorder=5)
    ax.plot(*proj_at([0, 0], [LX, LX], [Z_SHALLOW, float(z_fn(0, LX))], orig),
            color=PALETTE["ink_muted"], lw=0.60, ls=":", alpha=0.50, zorder=5)

    for y_ht in np.linspace(0.7, LX - 0.5, 13):
        z_ht = float(z_fn(0, y_ht))
        ax.plot(*proj_at([0, -0.15], [y_ht, y_ht - 0.14], [z_ht, z_ht + 0.04], orig),
                color=PALETTE["bed_edge"], lw=0.55, alpha=0.60, zorder=18)
    for x_ht in np.linspace(0.5, WY - 0.5, 11):
        z_ht = float(z_fn(x_ht, LX))
        ax.plot(*proj_at([x_ht, x_ht - 0.12], [LX, LX + 0.16], [z_ht, z_ht + 0.04], orig),
                color=PALETTE["bed_edge"], lw=0.55, alpha=0.60, zorder=18)

    # -----------------------------------------------------------------------
    # 2. Front-Left Stepped Geological Face & Front-Right Geological Face
    # -----------------------------------------------------------------------
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
    ax.add_patch(Polygon(
        [proj_at(*p, orig) for p in stepped_front_3d], closed=True,
        facecolor=PALETTE["bed_front"], edgecolor=PALETTE["bed_edge"],
        lw=1.05, alpha=0.97, zorder=12
    ))

    def front_bed_top_z(xv):
        return Z_DEEP if (XC_L < xv < XC_R) else Z_SHALLOW

    for xh in np.linspace(0.20, WY - 0.18, 36):
        for k_sub in range(3):
            x_s = np.clip(xh + (k_sub - 1) * 0.05, 0.08, WY - 0.08)
            if abs(x_s - XC_L) < 0.12 or abs(x_s - XC_R) < 0.12:
                continue
            zt = front_bed_top_z(x_s)
            zb = max(Z_BASE + 0.05, zt - 0.24 + 0.04 * k_sub)
            ax.plot(*proj_at([x_s, x_s - 0.11], [0, 0], [zt, zb], orig),
                    color=PALETTE["bed_hatch"], lw=0.48, alpha=0.68, zorder=12.5)

    for xh in np.concatenate([np.linspace(0.25, XC_L - 0.22, 11), np.linspace(XC_R + 0.22, WY - 0.20, 11)]):
        for z_layer in [-0.72, -1.08]:
            ax.plot(*proj_at([xh, xh - 0.11], [0, 0], [z_layer, z_layer - 0.20], orig),
                    color=PALETTE["bed_hatch"], lw=0.42, alpha=0.52, zorder=12.5)

    # Front-Right Geological Face (x = WY)
    pts_bed_fr = [
        proj_at(WY, 0, Z_SHALLOW, orig), proj_at(WY, LX, Z_SHALLOW, orig),
        proj_at(WY, LX, Z_BASE, orig), proj_at(WY, 0, Z_BASE, orig),
    ]
    ax.add_patch(Polygon(
        pts_bed_fr, closed=True,
        facecolor=PALETTE["bed_right"], edgecolor=PALETTE["bed_edge"],
        lw=1.00, alpha=0.97, zorder=12
    ))

    for yh in np.linspace(0.30, LX - 0.30, 30):
        for k_sub in range(3):
            y_s = np.clip(yh + (k_sub - 1) * 0.06, 0.08, LX - 0.08)
            ax.plot(*proj_at([WY, WY], [y_s, y_s - 0.13], [Z_SHALLOW, Z_SHALLOW - 0.25 + 0.04 * k_sub], orig),
                    color="#736354", lw=0.48, alpha=0.65, zorder=12.5)
        for z_layer in [-0.75, -1.10]:
            ax.plot(*proj_at([WY, WY], [yh, yh - 0.13], [z_layer, z_layer - 0.20], orig),
                    color="#736354", lw=0.42, alpha=0.48, zorder=12.5)

    # -----------------------------------------------------------------------
    # 3. Translucent Front & Side Water Column Cutaways
    # -----------------------------------------------------------------------
    xg_L = np.linspace(0, XC_L, 24)
    xg_R = np.linspace(XC_R, WY, 24)
    xg_C = np.linspace(XC_L, XC_R, 20)

    for xg_seg in [xg_L, xg_R]:
        pts_w = (
            [proj_at(x_, 0, z_fn(x_, 0), orig) for x_ in xg_seg]
            + [proj_at(xg_seg[-1], 0, Z_SHALLOW, orig), proj_at(xg_seg[0], 0, Z_SHALLOW, orig)]
        )
        ax.add_patch(Polygon(
            pts_w, closed=True,
            facecolor=PALETTE["water_front"], edgecolor="none",
            alpha=0.52 if mode == "high" else 0.65, zorder=13
        ))

    pts_w_C = (
        [proj_at(x_, 0, z_fn(x_, 0), orig) for x_ in xg_C]
        + [proj_at(XC_R, 0, Z_DEEP, orig), proj_at(XC_L, 0, Z_DEEP, orig)]
    )
    ax.add_patch(Polygon(
        pts_w_C, closed=True,
        facecolor=PALETTE["water_channel"], edgecolor="none", alpha=0.60, zorder=13.2
    ))

    pts_w_fr = (
        [proj_at(WY, y_, z_fn(WY, y_), orig) for y_ in yg]
        + [proj_at(WY, LX, Z_SHALLOW, orig), proj_at(WY, 0, Z_SHALLOW, orig)]
    )
    ax.add_patch(Polygon(
        pts_w_fr, closed=True,
        facecolor=PALETTE["water_right"], edgecolor="none",
        alpha=0.50 if mode == "high" else 0.65, zorder=13
    ))

    # -----------------------------------------------------------------------
    # 4. Free Surface Mesh & Intertidal Drying Zones (in Low Tide)
    # -----------------------------------------------------------------------
    XX, YY = np.meshgrid(xg, yg, indexing="ij")
    ZZ = z_fn(XX, YY)

    if mode == "high":
        shelf_cmap = LinearSegmentedColormap.from_list("high_shelf", ["#8AB4CE", "#B8D6E8", "#E2F0F8"])
        chan_cmap = LinearSegmentedColormap.from_list("high_chan", ["#4A7FA2", "#6EA1C3", "#A6CCE3"])
    else:
        # In low tide, shallow shelves have a pale translucent thin-film look with wet sand showing through!
        shelf_cmap = LinearSegmentedColormap.from_list("low_shelf", ["#D8CEBF", "#CEDDE4", "#DCEAF2"])
        chan_cmap = LinearSegmentedColormap.from_list("low_chan", ["#4E82A5", "#76A8C8", "#AED0E5"])

    z_min, z_max = ZZ.min(), ZZ.max()

    for i in range(nx_pts - 1):
        for j in range(ny_pts - 1):
            xs = [XX[i, j], XX[i + 1, j], XX[i + 1, j + 1], XX[i, j + 1]]
            ys = [YY[i, j], YY[i + 1, j], YY[i + 1, j + 1], YY[i, j + 1]]
            zs = [ZZ[i, j], ZZ[i + 1, j], ZZ[i + 1, j + 1], ZZ[i, j + 1]]
            X2, Y2 = proj_at(xs, ys, zs, orig)
            x_m = 0.25 * sum(xs)
            y_m = 0.25 * sum(ys)
            z_m = 0.25 * sum(zs)
            in_chan = (XC_L <= x_m <= XC_R)

            if mode == "high":
                norm_z = (z_m - z_min) / (z_max - z_min + 1e-9)
                col = chan_cmap(0.65 * norm_z + 0.25) if in_chan else shelf_cmap(0.65 * norm_z + 0.25)
                alp = 0.84 if in_chan else 0.76
            else:
                if in_chan:
                    col = chan_cmap(0.55)
                    alp = 0.84
                else:
                    # Near outer lateral margins at mid-basin, show exposed/nearly-dry intertidal sandbank!
                    dist_edge = min(x_m, WY - x_m)
                    dry_factor = np.exp(-((dist_edge / 0.85) ** 2)) * np.exp(-(((y_m - 4.8) / 3.2) ** 2))
                    col = shelf_cmap(1.0 - 0.88 * dry_factor)
                    alp = 0.62 if dry_factor < 0.45 else 0.82

            ax.add_patch(Polygon(
                list(zip(X2, Y2)),
                facecolor=col, edgecolor=col, lw=0.08, alpha=alp, zorder=15
            ))

    # Fine computational grid mesh (60 x 120 cells)
    for i in range(0, nx_pts, 3):
        ax.plot(*proj_at(XX[i, :], YY[i, :], ZZ[i, :], orig),
                color=PALETTE["water_mesh"], lw=0.35, alpha=0.50, zorder=15.5)
    for j in range(0, ny_pts, 3):
        ax.plot(*proj_at(XX[:, j], YY[:, j], ZZ[:, j], orig),
                color=PALETTE["water_mesh"], lw=0.35, alpha=0.50, zorder=15.5)

    # Dashed submerged channel bank lines projected on water surface
    for x_bank in [XC_L, XC_R]:
        ax.plot(*proj_at(np.full(ny_pts, x_bank), yg, z_fn(x_bank, yg), orig),
                color=PALETTE["navy_deep"], lw=0.95, ls="--", alpha=0.82, zorder=16)

    # In Low Tide, draw dashed contour of intertidal drying patches ("zonas sujeitas a secagem")
    if mode == "low":
        th_p = np.linspace(0, 2 * np.pi, 50)
        for (xc_dry, yc_dry, rx_d, ry_d) in [(0.52, 4.9, 0.42, 1.85), (WY - 0.52, 5.1, 0.42, 1.85)]:
            xs_d = np.clip(xc_dry + rx_d * np.cos(th_p), 0.06, WY - 0.06)
            ys_d = yc_dry + ry_d * np.sin(th_p)
            zs_d = z_fn(xs_d, ys_d) + 0.005
            ax.plot(*proj_at(xs_d, ys_d, zs_d, orig),
                    color=PALETTE["bed_edge"], lw=0.90, ls=":", alpha=0.85, zorder=16.5)

    # -----------------------------------------------------------------------
    # 5. Structural Foreground Edges & Undisturbed Datum Plane z = 0!
    #    Crucial: In High Tide, water is ABOVE z = 0; in Low Tide, water is BELOW z = 0!
    # -----------------------------------------------------------------------
    ax.plot(*proj_at(xg, np.zeros(nx_pts), z_fn(xg, 0), orig),
            color=PALETTE["water_edge"], lw=1.45, zorder=17)
    ax.plot(*proj_at(np.full(ny_pts, WY), yg, z_fn(WY, yg), orig),
            color=PALETTE["water_edge"], lw=1.40, zorder=17)

    stepped_edge_x = [0, XC_L, XC_L, XC_R, XC_R, WY]
    stepped_edge_z = [Z_SHALLOW, Z_SHALLOW, Z_DEEP, Z_DEEP, Z_SHALLOW, Z_SHALLOW]
    ax.plot(*proj_at(stepped_edge_x, np.zeros(6), stepped_edge_z, orig),
            color=PALETTE["bed_edge"], lw=1.50, zorder=17.5)

    # Vertical edges extending up to max(0.0, z_fn) so the z = 0 datum wireframe is crystal clear!
    for (xc_e, yc_e), lw_e in [((0, 0), 1.15), ((WY, 0), 1.30), ((WY, LX), 1.05)]:
        z_top_edge = max(0.05, float(z_fn(xc_e, yc_e)))
        ax.plot(*proj_at([xc_e, xc_e], [yc_e, yc_e], [Z_BASE, float(z_fn(xc_e, yc_e))], orig),
                color=PALETTE["water_edge"], lw=lw_e, zorder=17)
        if mode == "low":
            # Dotted ghost wireframe from low-tide water up to z = 0 datum!
            ax.plot(*proj_at([xc_e, xc_e], [yc_e, yc_e], [float(z_fn(xc_e, yc_e)), 0.0], orig),
                    color=PALETTE["rule_dark"], lw=0.75, ls=":", alpha=0.70, zorder=17)

    # Reference Datum Plane z = 0 dashed contour on Front and Right faces!
    ax.plot(*proj_at([0, WY], [0, 0], [0, 0], orig),
            color=PALETTE["rule_dark"], lw=1.05, ls=(0, (4, 3)), zorder=18)
    ax.plot(*proj_at([WY, WY], [0, LX], [0, 0], orig),
            color=PALETTE["rule_dark"], lw=0.95, ls=(0, (4, 3)), zorder=18)

    # -----------------------------------------------------------------------
    # 6. Hydrodynamic Flow Vectors & Piston Action (Flood vs. Ebb)
    # -----------------------------------------------------------------------
    if mode == "high":
        # FLOOD TIDE: Strong inflow arrows up the deep channel (fast wave, low friction)
        for (ya, yb, lw_v) in [(-0.55, 2.75, 2.45), (3.05, 6.25, 2.15), (6.55, 8.95, 1.85)]:
            draw_3d_arrow_at(
                ax, (xc_mid, ya, z_fn(xc_mid, max(0, ya)) + 0.03),
                (xc_mid, yb, z_fn(xc_mid, yb) + 0.03),
                orig, color=PALETTE["navy_deep"], lw=lw_v, mutation_scale=13.0, zorder=22
            )
        # Overflow arrows from channel onto shallow flats!
        for y_sp, x_dest_L, x_dest_R in [(1.8, 0.95, 6.25), (4.6, 0.85, 6.35), (7.3, 1.05, 6.15)]:
            p0_L = proj_at(XC_L + 0.08, y_sp, z_fn(XC_L, y_sp) + 0.03, orig)
            p1_L = proj_at(x_dest_L, y_sp + 1.10, z_fn(x_dest_L, y_sp + 1.10) + 0.03, orig)
            draw_2d_arrow(ax, p0_L, p1_L, color=PALETTE["z_node"], lw=1.55,
                          mutation_scale=10.5, connectionstyle="arc3,rad=0.22", zorder=21)

            p0_R = proj_at(XC_R - 0.08, y_sp, z_fn(XC_R, y_sp) + 0.03, orig)
            p1_R = proj_at(x_dest_R, y_sp + 1.10, z_fn(x_dest_R, y_sp + 1.10) + 0.03, orig)
            draw_2d_arrow(ax, p0_R, p1_R, color=PALETTE["z_node"], lw=1.55,
                          mutation_scale=10.5, connectionstyle="arc3,rad=-0.22", zorder=21)
    else:
        # EBB TIDE: Drainage arrows from shallow flats back into the central channel,
        # and strong outflow arrows exiting the open channel mouth!
        for (ya, yb, lw_v) in [(8.85, 6.25, 1.85), (5.95, 2.85, 2.15), (2.55, -0.75, 2.50)]:
            draw_3d_arrow_at(
                ax, (xc_mid, ya, z_fn(xc_mid, ya) + 0.03),
                (xc_mid, yb, z_fn(xc_mid, max(0, yb)) + 0.03),
                orig, color=PALETTE["navy_deep"], lw=lw_v, mutation_scale=13.0, zorder=22
            )
        # Lateral drainage arrows converging from flats back into the channel!
        for y_sp, x_src_L, x_src_R in [(2.6, 1.15, 6.05), (5.4, 1.05, 6.15), (8.0, 1.25, 5.95)]:
            p0_L = proj_at(x_src_L, y_sp, z_fn(x_src_L, y_sp) + 0.03, orig)
            p1_L = proj_at(XC_L - 0.06, y_sp - 1.05, z_fn(XC_L, y_sp - 1.05) + 0.03, orig)
            draw_2d_arrow(ax, p0_L, p1_L, color=PALETTE["teal_adi"], lw=1.45,
                          mutation_scale=10.0, connectionstyle="arc3,rad=0.18", zorder=21)

            p0_R = proj_at(x_src_R, y_sp, z_fn(x_src_R, y_sp) + 0.03, orig)
            p1_R = proj_at(XC_R + 0.06, y_sp - 1.05, z_fn(XC_R, y_sp - 1.05) + 0.03, orig)
            draw_2d_arrow(ax, p0_R, p1_R, color=PALETTE["teal_adi"], lw=1.45,
                          mutation_scale=10.0, connectionstyle="arc3,rad=-0.18", zorder=21)

        # Opposing bottom friction vectors (-gamma u) on the 10 cm film flats!
        for (xf_r, yf_r, sgn_r) in [(1.55, 2.0, -1), (5.65, 2.2, +1)]:
            pf0 = proj_at(xf_r, yf_r, Z_SHALLOW + 0.015, orig)
            pf1 = proj_at(xf_r + sgn_r * 0.68, yf_r + 0.35, Z_SHALLOW + 0.015, orig)
            draw_2d_arrow(ax, pf0, pf1, color=PALETTE["terracotta"], lw=1.35,
                          mutation_scale=8.5, ls="-", zorder=21.5)


def draw_tidal_piston_gauge(ax, x0, y0, w, h, mode="high", zorder=22):
    """
    Draw a crisp coastal-engineering M_2 Tidal Harmonic Gauge (z_borda(t) over 12 h)
    to the left of each basin, highlighting either the High Tide crest (+0.4 m)
    or Low Tide trough (-0.4 m) acting as the slow open-boundary piston!
    """
    ax.add_patch(Rectangle(
        (x0, y0), w, h,
        facecolor="#FFFFFF", edgecolor=PALETTE["rule_dark"], lw=0.95, zorder=zorder
    ))
    ym = y0 + 0.50 * h
    ax.plot([x0 + 0.12, x0 + w - 0.12], [ym, ym],
            color=PALETTE["rule_dark"], lw=0.75, ls="--", zorder=zorder + 1)
    crisp_text(ax, x0 + 0.10, ym, r"$0$", color=PALETTE["ink_muted"], stroke_w=0.13,
               fontsize=7.6, ha="right", va="center", zorder=zorder + 3)

    ts = np.linspace(0, 2 * np.pi, 100)
    xs_c = x0 + 0.16 + (ts / (2 * np.pi)) * (w - 0.32)
    amp_y = 0.23 * h
    ys_c = ym + amp_y * np.sin(ts)
    ax.plot(xs_c, ys_c, color=PALETTE["navy_deep"], lw=1.55, zorder=zorder + 2)

    if mode == "high":
        # Highlight crest at t = 3 h (pi/2) — label cleanly above the crest dot
        xp = x0 + 0.16 + 0.25 * (w - 0.32)
        yp = ym + amp_y
        col_hl = PALETTE["z_node"]
        lbl_pt = r"$+0{,}4\text{ m}$"
        va_pt = "bottom"
        dy_pt = 0.05
    else:
        # Highlight trough at t = 9 h (3*pi/2) — label cleanly below the trough dot
        xp = x0 + 0.16 + 0.75 * (w - 0.32)
        yp = ym - amp_y
        col_hl = PALETTE["terracotta"]
        lbl_pt = r"$-0{,}4\text{ m}$"
        va_pt = "top"
        dy_pt = -0.05

    ax.plot([xp, xp], [ym, yp], color=col_hl, lw=1.25, ls=":", zorder=zorder + 2)
    ax.plot(xp, yp, marker="o", markersize=6.2, markerfacecolor=col_hl,
            markeredgecolor="white", markeredgewidth=1.0, zorder=zorder + 4)
    crisp_text(ax, xp, yp + dy_pt, lbl_pt,
               color=col_hl, stroke_w=0.17,
               fontsize=8.0, fontweight="bold",
               ha="center", va=va_pt, zorder=zorder + 5)

    # X-axis labels 0h, 6h, 12h
    for frac, t_str in [(0.0, r"$0\text{h}$"), (0.5, r"$6\text{h}$"), (1.0, r"$12\text{h}$")]:
        xt = x0 + 0.16 + frac * (w - 0.32)
        ax.plot([xt, xt], [y0, y0 + 0.06], color=PALETTE["rule_dark"], lw=0.75, zorder=zorder + 2)
        crisp_text(ax, xt, y0 - 0.06, t_str, color=PALETTE["ink_secondary"], stroke_w=0.13,
                   fontsize=7.5, ha="center", va="top", zorder=zorder + 3)

    crisp_text(
        ax, x0 + 0.5 * w, y0 + h + 0.08,
        r"Pistão de Maré $M_2$ ($T = 12\text{ h}$)",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=8.1, fontweight="bold", ha="center", va="bottom", zorder=zorder + 4
    )


def build_figure():
    # Generous two-tier vertical coastal-engineering monograph layout
    fig, ax = plt.subplots(figsize=(15.6, 12.8), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    ORIG_TOP = (-2.55, 3.65)   # Top Basin: High Tide (+0.4 m)
    ORIG_BOT = (-2.55, -4.35)  # Bottom Basin: Low Tide (-0.4 m)
    xc_mid = 0.5 * (XC_L + XC_R)

    # =======================================================================
    # CELESTIAL 12-HOUR CYCLE ARC AT VERY TOP (Framing the Semidiurnal Period)
    # =======================================================================
    x_sun_L, y_sun_L = -4.85, 6.85
    x_sun_M, y_sun_M = 1.65, 8.45
    x_sun_R, y_sun_R = 8.15, 6.85

    s_arc = np.linspace(0, 1, 120)
    P0_s = np.array([x_sun_L, y_sun_L])
    P2_s = np.array([x_sun_R, y_sun_R])
    Pm_s = np.array([x_sun_M, y_sun_M])
    P1_s = 2.0 * Pm_s - 0.5 * (P0_s + P2_s)
    arc_pts = (
        ((1 - s_arc) ** 2)[:, None] * P0_s
        + (2 * (1 - s_arc) * s_arc)[:, None] * P1_s
        + (s_arc ** 2)[:, None] * P2_s
    )
    ax.plot(arc_pts[:, 0], arc_pts[:, 1],
            color=PALETTE["amber_sun"], lw=1.35, ls=(0, (5, 3)), alpha=0.88, zorder=19)

    for s_arr in [0.26, 0.74]:
        pa = (1 - s_arr) ** 2 * P0_s + 2 * (1 - s_arr) * s_arr * P1_s + (s_arr ** 2) * P2_s
        sn = s_arr + 0.02
        pb = (1 - sn) ** 2 * P0_s + 2 * (1 - sn) * sn * P1_s + (sn ** 2) * P2_s
        draw_2d_arrow(ax, tuple(pa), tuple(pb), color=PALETTE["amber_sun"], lw=1.35, mutation_scale=9.0, zorder=20)

    draw_stylized_sun(ax, x_sun_L, y_sun_L, color=PALETTE["amber_sun"])
    crisp_text(ax, x_sun_L, y_sun_L - 0.28, r"$t = 0\text{ h}$",
               color=PALETTE["amber_sun"], stroke_w=0.16, bg_clear=True, pad=0.03,
               fontsize=8.2, fontweight="bold", ha="center", va="top", zorder=26)

    draw_stylized_sun(ax, x_sun_M, y_sun_M, color=PALETTE["amber_sun"])
    crisp_text(ax, x_sun_M, y_sun_M + 0.28, r"$t = 6\text{ h}$",
               color=PALETTE["amber_sun"], stroke_w=0.16, bg_clear=True, pad=0.03,
               fontsize=8.3, fontweight="bold", ha="center", va="bottom", zorder=26)

    draw_stylized_sun(ax, x_sun_R, y_sun_R, color=PALETTE["amber_sun"])
    crisp_text(ax, x_sun_R, y_sun_R - 0.28, r"$t = 12\text{ h}$",
               color=PALETTE["amber_sun"], stroke_w=0.16, bg_clear=True, pad=0.03,
               fontsize=8.2, fontweight="bold", ha="center", va="top", zorder=26)

    crisp_text(
        ax, x_sun_M, y_sun_M - 0.34,
        r"Ciclo Semidiurno $M_2$: $T = 12\text{ h}$ ($720$ passos de $\Delta t = 60\text{ s}$) — Pistão lento na fronteira aberta",
        color=PALETTE["amber_sun"], stroke_w=0.16, bg_clear=True, pad=0.05,
        fontsize=8.6, fontweight="bold", fontstyle="italic", ha="center", va="top", zorder=26
    )

    # =======================================================================
    # TOP PANEL: ESTÁGIO A — MARÉ ALTA / ENCHENTE (+0.4 m -> H_rasa = 0.9 m)
    # =======================================================================
    draw_basin_state(ax, ORIG_TOP, mode="high")

    # Stage A Header Title (upper-left of Top Basin)
    crisp_text(
        ax, -6.75, 6.08,
        r"1. Maré Alta / Enchente ($z = +0{,}4\text{ m}$)",
        color=PALETTE["navy_deep"], stroke_w=0.20,
        fontsize=10.6, fontweight="bold", ha="left", va="bottom", zorder=28
    )
    crisp_text(
        ax, -6.75, 5.82,
        "Entrada rápida pelo canal profundo\n"
        "e transbordamento para as planícies",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=8.5, fontstyle="italic", ha="left", va="top", linespacing=1.20, zorder=28
    )

    # Tidal Piston Gauge for High Tide (elevated in left margin with wide clearance!)
    draw_tidal_piston_gauge(ax, x0=-6.75, y0=3.92, w=2.35, h=1.26, mode="high")

    # Piston Push Arrow from Gauge toward Channel Entrance
    p_mouth_top = proj_at(xc_mid, 0.0, 0.14, ORIG_TOP)
    draw_2d_arrow(
        ax, (-4.28, 4.35), (p_mouth_top[0] - 0.85, p_mouth_top[1] - 0.05),
        color=PALETTE["navy_deep"], lw=1.6, mutation_scale=11.0,
        connectionstyle="arc3,rad=0.18", zorder=24
    )
    crisp_text(
        ax, -2.85, 2.35,
        r"Pistão empurra água ($+0{,}4\text{ m}$)",
        color=PALETTE["navy_deep"], stroke_w=0.16, bg_clear=True, pad=0.04,
        fontsize=8.2, fontweight="bold", ha="right", va="top", zorder=26
    )

    # Front Shelf Total Depth Dimension in High Tide: H = 0.5 + 0.4 = 0.9 m!
    x_dim_sh = 0.65
    z_top_sh_H = float(z_surf_high_tide(x_dim_sh, 0))
    p_ht_top = proj_at(x_dim_sh, 0, z_top_sh_H, ORIG_TOP)
    p_ht_bot = proj_at(x_dim_sh, 0, Z_SHALLOW, ORIG_TOP)
    draw_2d_arrow(ax, p_ht_bot, p_ht_top, color=PALETTE["navy_deep"], lw=1.25,
                  mutation_scale=7.5, arrowstyle="<|-|>", zorder=24)

    # Also show +0.4 m elevation above z = 0 on the front-left shelf!
    p_z0_sh = proj_at(1.55, 0, 0.0, ORIG_TOP)
    p_ztop_sh = proj_at(1.55, 0, float(z_surf_high_tide(1.55, 0)), ORIG_TOP)
    draw_2d_arrow(ax, p_z0_sh, p_ztop_sh, color=PALETTE["z_node"], lw=1.15,
                  mutation_scale=6.5, arrowstyle="<|-|>", zorder=24)

    p_sh_mid_H = (0.5 * (p_ht_top[0] + p_ht_bot[0]), 0.5 * (p_ht_top[1] + p_ht_bot[1]))
    ax.plot([p_sh_mid_H[0] - 0.06, -3.45], [p_sh_mid_H[1], 3.12],
            color=PALETTE["navy_deep"], lw=0.85, zorder=23)
    crisp_text(
        ax, -3.52, 3.12,
        r"Planície inundada: $H = 0{,}9\text{ m}$" + "\n"
        + r"($0{,}5\text{ m} + 0{,}4\text{ m}$)",
        color=PALETTE["navy_deep"], stroke_w=0.16, bg_clear=True, pad=0.05,
        fontsize=8.3, fontweight="bold", ha="right", va="center", linespacing=1.18, zorder=26
    )

    # Deep Channel Total Depth in High Tide: H = 5.4 m (c = sqrt(gH) alta, pouco atrito)
    x_ch_d = XC_R - 0.25
    p_ch_tH = proj_at(x_ch_d, 0, float(z_surf_high_tide(x_ch_d, 0)), ORIG_TOP)
    p_ch_bH = proj_at(x_ch_d, 0, Z_DEEP, ORIG_TOP)
    draw_2d_arrow(ax, p_ch_bH, p_ch_tH, color="#FFFFFF", lw=1.4, mutation_scale=8.0, arrowstyle="<|-|>", zorder=23)
    draw_2d_arrow(ax, p_ch_bH, p_ch_tH, color=PALETTE["navy_deep"], lw=1.15, mutation_scale=7.5, arrowstyle="<|-|>", zorder=24)
    crisp_text(
        ax, proj_at(XC_R + 0.18, 0, 0.55 * Z_DEEP, ORIG_TOP)[0],
        proj_at(XC_R + 0.18, 0, 0.55 * Z_DEEP, ORIG_TOP)[1],
        r"Canal cheio: $H = 5{,}4\text{ m}$",
        color=PALETTE["navy_deep"], stroke_w=0.17, bg_color=PALETTE["bed_front"], pad=0.04,
        fontsize=8.2, fontweight="bold", ha="left", va="center", zorder=25
    )

    # Callout on Top Basin Right Margin: Fast channel propagation & lateral overflow (in open cream space above basin!)
    p_ov_target = proj_at(4.95, 5.10, float(z_surf_high_tide(4.95, 5.10)), ORIG_TOP)
    p_ov_lbl = (7.15, 5.25)
    ax.plot(*p_ov_target, marker="o", markersize=3.8, color=PALETTE["navy_deep"], zorder=25)
    draw_2d_arrow(ax, (p_ov_lbl[0] - 0.10, p_ov_lbl[1] - 0.06), p_ov_target,
                  color=PALETTE["navy_deep"], lw=0.90, mutation_scale=8.0,
                  connectionstyle="arc3,rad=0.14", zorder=24)
    crisp_text(
        ax, p_ov_lbl[0], p_ov_lbl[1],
        r"Alta velocidade no canal ($C_r = 8$)" + "\n"
        + r"Pouco atrito $\rightarrow$ onda viaja rápido" + "\n"
        + r"e transborda para as laterais",
        color=PALETTE["navy_deep"], stroke_w=0.16, bg_clear=True, pad=0.06,
        fontsize=8.2, fontweight="bold", ha="left", va="center", linespacing=1.22, zorder=26
    )

    # Datum z = 0 note on Top Basin front-right
    p_dat_top = proj_at(WY, 0.45, 0.0, ORIG_TOP)
    ax.plot(p_dat_top[0], p_dat_top[1], marker="o", markersize=3.3, color=PALETTE["rule_dark"], zorder=24)
    ax.plot([p_dat_top[0], p_dat_top[0] + 0.75], [p_dat_top[1], p_dat_top[1] - 0.16],
            color=PALETTE["rule_dark"], lw=0.85, ls="--", zorder=23)
    crisp_text(
        ax, p_dat_top[0] + 0.80, p_dat_top[1] - 0.18,
        r"Nível médio $z = 0$ (água $+0{,}4\text{ m}$ acima)",
        color=PALETTE["rule_dark"], stroke_w=0.15, bg_clear=True, pad=0.03,
        fontsize=8.0, fontstyle="italic", ha="left", va="center", zorder=25
    )

    # Closed boundary labels on Top Basin
    p_mL_top = proj_at(0, 4.8, 0.30, ORIG_TOP)
    crisp_text(ax, p_mL_top[0] - 0.20, p_mL_top[1] + 0.12, r"Margem fechada ($u_n = 0$)",
               color=PALETTE["bed_edge"], stroke_w=0.14, bg_clear=True, pad=0.03,
               fontsize=7.9, fontweight="bold", fontstyle="italic", ha="right", va="bottom", zorder=25)
    p_mB_top = proj_at(1.75, LX, 0.30, ORIG_TOP)
    crisp_text(ax, p_mB_top[0] + 0.05, p_mB_top[1] + 0.22, r"Cabeceira fechada ($u_n = 0$)",
               color=PALETTE["bed_edge"], stroke_w=0.14, bg_clear=True, pad=0.03,
               fontsize=7.9, fontweight="bold", fontstyle="italic", ha="center", va="bottom", zorder=25)

    # =======================================================================
    # SUBTLE TRANSITION DIVIDER BETWEEN HIGH TIDE AND LOW TIDE (6 h half-cycle)
    #    Placed strictly in the open whitespace below Top Basin's lowest corner!
    # =======================================================================
    y_mid_div = 0.08
    ax.plot([-6.75, 9.65], [y_mid_div, y_mid_div], color=PALETTE["rule_light"], lw=0.95, ls="--", zorder=10)
    crisp_text(
        ax, 1.55, y_mid_div,
        r"$\Downarrow\;$ Meio período depois ($\Delta t_{\mathrm{maré}} = 6\text{ h}$): inversão do pistão na fronteira aberta $\;\Downarrow$",
        color=PALETTE["amber_sun"], stroke_w=0.16, bg_clear=True, pad=0.10,
        fontsize=8.4, fontweight="bold", ha="center", va="center", zorder=25
    )

    # =======================================================================
    # BOTTOM PANEL: ESTÁGIO B — MARÉ BAIXA / VAZANTE (-0.4 m -> H_rasa = 0.1 m = 10 cm)
    # =======================================================================
    draw_basin_state(ax, ORIG_BOT, mode="low")

    # Stage B Header Title (upper-left of Bottom Basin)
    crisp_text(
        ax, -6.75, -1.35,
        r"2. Maré Baixa / Vazante ($z = -0{,}4\text{ m}$)",
        color=PALETTE["terracotta"], stroke_w=0.20,
        fontsize=10.6, fontweight="bold", ha="left", va="bottom", zorder=28
    )
    crisp_text(
        ax, -6.75, -1.62,
        "Recuo da água para o canal central\n"
        "e película rasa crítica nas laterais",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=8.5, fontstyle="italic", ha="left", va="top", linespacing=1.20, zorder=28
    )

    # Tidal Piston Gauge for Low Tide (elevated in left margin with wide clearance!)
    draw_tidal_piston_gauge(ax, x0=-6.75, y0=-3.62, w=2.35, h=1.26, mode="low")

    # Piston Pull Arrow from Channel Entrance out toward the Sea/Gauge
    p_mouth_bot = proj_at(xc_mid, -0.45, -0.28, ORIG_BOT)
    draw_2d_arrow(
        ax, (p_mouth_bot[0] - 0.25, p_mouth_bot[1] - 0.10), (-4.28, -3.25),
        color=PALETTE["terracotta"], lw=1.6, mutation_scale=11.0,
        connectionstyle="arc3,rad=-0.20", zorder=24
    )
    crisp_text(
        ax, -2.85, -5.58,
        r"Água recua pela boca ($-0{,}4\text{ m}$)",
        color=PALETTE["terracotta"], stroke_w=0.16, bg_clear=True, pad=0.04,
        fontsize=8.2, fontweight="bold", ha="right", va="top", zorder=26
    )

    # Front Shelf Thin Film Dimension in Low Tide: H = 0.5 - 0.4 = 0.1 m (10 cm)!
    z_top_sh_L = float(z_surf_low_tide(x_dim_sh, 0))
    p_lt_top = proj_at(x_dim_sh, 0, z_top_sh_L, ORIG_BOT)
    p_lt_bot = proj_at(x_dim_sh, 0, Z_SHALLOW, ORIG_BOT)
    p_lt_z0 = proj_at(1.45, 0, 0.0, ORIG_BOT)
    p_lt_zsurf = proj_at(1.45, 0, float(z_surf_low_tide(1.45, 0)), ORIG_BOT)

    # Draw -0.4 m drop arrow from z = 0 down to low-tide surface
    draw_2d_arrow(ax, p_lt_z0, p_lt_zsurf, color=PALETTE["terracotta"], lw=1.15,
                  mutation_scale=6.5, arrowstyle="<|-|>", zorder=24)

    # Pointer to the razor-thin 10 cm water film (comfortably below the gauge!)
    p_film_mid = (0.5 * (p_lt_top[0] + p_lt_bot[0]), 0.5 * (p_lt_top[1] + p_lt_bot[1]))
    ax.plot(p_film_mid[0], p_film_mid[1], marker="o", markersize=3.5, color=PALETTE["terracotta"], zorder=25)
    ax.plot([p_film_mid[0] - 0.05, -3.45], [p_film_mid[1], -4.62],
            color=PALETTE["terracotta"], lw=0.90, zorder=23)
    crisp_text(
        ax, -3.52, -4.62,
        r"Película rasa: $H = 0{,}1\text{ m}$ ($10\text{ cm}$)" + "\n"
        + r"($0{,}5\text{ m} - 0{,}4\text{ m}$: atrito domina)",
        color=PALETTE["terracotta"], stroke_w=0.16, bg_clear=True, pad=0.05,
        fontsize=8.3, fontweight="bold", ha="right", va="center", linespacing=1.18, zorder=26
    )

    # Deep Channel Total Depth in Low Tide: H = 4.6 m
    p_ch_tL = proj_at(x_ch_d, 0, float(z_surf_low_tide(x_ch_d, 0)), ORIG_BOT)
    p_ch_bL = proj_at(x_ch_d, 0, Z_DEEP, ORIG_BOT)
    draw_2d_arrow(ax, p_ch_bL, p_ch_tL, color="#FFFFFF", lw=1.4, mutation_scale=8.0, arrowstyle="<|-|>", zorder=23)
    draw_2d_arrow(ax, p_ch_bL, p_ch_tL, color=PALETTE["navy_deep"], lw=1.15, mutation_scale=7.5, arrowstyle="<|-|>", zorder=24)
    crisp_text(
        ax, proj_at(XC_R + 0.18, 0, 0.62 * Z_DEEP, ORIG_BOT)[0],
        proj_at(XC_R + 0.18, 0, 0.62 * Z_DEEP, ORIG_BOT)[1],
        r"Canal em vazante: $H = 4{,}6\text{ m}$",
        color=PALETTE["navy_deep"], stroke_w=0.17, bg_color=PALETTE["bed_front"], pad=0.04,
        fontsize=8.2, fontweight="bold", ha="left", va="center", zorder=25
    )

    # Callout 1 on Bottom Basin Right Margin: Wetting & Drying + Bottom Friction (-gamma u) (in open cream space!)
    p_dry_target = proj_at(WY - 0.52, 5.10, float(z_surf_low_tide(WY - 0.52, 5.10)), ORIG_BOT)
    p_dry_lbl = (6.55, -2.25)
    ax.plot(*p_dry_target, marker="o", markersize=3.8, color=PALETTE["terracotta"], zorder=25)
    draw_2d_arrow(ax, (p_dry_lbl[0] - 0.10, p_dry_lbl[1] - 0.08), p_dry_target,
                  color=PALETTE["terracotta"], lw=0.90, mutation_scale=8.0,
                  connectionstyle="arc3,rad=0.16", zorder=24)
    crisp_text(
        ax, p_dry_lbl[0], p_dry_lbl[1],
        r"Molhamento e secagem ($H \rightarrow 0$)" + "\n"
        + r"Forte atrito $-\gamma\mathbf{u}$ nas planícies;" + "\n"
        + r"esquema mantém estabilidade",
        color=PALETTE["terracotta"], stroke_w=0.16, bg_clear=True, pad=0.06,
        fontsize=8.2, fontweight="bold", ha="left", va="center", linespacing=1.22, zorder=26
    )

    # Callout 2 on Bottom Basin Upper-Left Margin: Computational Mesh (60 x 120 cells) (in open cream space!)
    p_mesh_b = proj_at(1.85, 5.60, float(z_surf_low_tide(1.85, 5.60)), ORIG_BOT)
    p_mesh_lbl_b = (-0.55, -2.25)
    ax.plot(*p_mesh_b, marker="o", markersize=3.6, color=PALETTE["navy_deep"], zorder=25)
    draw_2d_arrow(ax, (p_mesh_lbl_b[0] + 0.10, p_mesh_lbl_b[1] - 0.05), p_mesh_b,
                  color=PALETTE["navy_deep"], lw=0.85, mutation_scale=7.5,
                  connectionstyle="arc3,rad=-0.14", zorder=24)
    crisp_text(
        ax, p_mesh_lbl_b[0], p_mesh_lbl_b[1],
        r"Malha $60 \times 120$ ($\Delta x = \Delta y = 50\text{ m}$)",
        color=PALETTE["navy_deep"], stroke_w=0.16, bg_clear=True, pad=0.05,
        fontsize=8.2, fontweight="bold", ha="right", va="center", zorder=26
    )

    # Datum z = 0 note on Bottom Basin front-right (showing water dropped -0.4 m BELOW z = 0!)
    p_dat_bot = proj_at(WY, 0.45, 0.0, ORIG_BOT)
    ax.plot(p_dat_bot[0], p_dat_bot[1], marker="o", markersize=3.3, color=PALETTE["rule_dark"], zorder=24)
    ax.plot([p_dat_bot[0], p_dat_bot[0] + 0.75], [p_dat_bot[1], p_dat_bot[1] - 0.14],
            color=PALETTE["rule_dark"], lw=0.85, ls="--", zorder=23)
    crisp_text(
        ax, p_dat_bot[0] + 0.80, p_dat_bot[1] - 0.16,
        r"Nível médio $z = 0$ (água $-0{,}4\text{ m}$ abaixo)",
        color=PALETTE["rule_dark"], stroke_w=0.15, bg_clear=True, pad=0.03,
        fontsize=8.0, fontstyle="italic", ha="left", va="center", zorder=25
    )

    # =======================================================================
    # SHARED ENGINEERING DIMENSIONS BELOW THE BOTTOM BASIN (Clean & Uncluttered)
    # =======================================================================
    # 1. Channel Width: 300 m (cleanly inside the front geological face above Z_BASE!)
    p_cw_L = proj_at(XC_L, 0, Z_DEEP - 0.14, ORIG_BOT)
    p_cw_R = proj_at(XC_R, 0, Z_DEEP - 0.14, ORIG_BOT)
    ax.plot(*proj_at([XC_L, XC_L], [0, 0], [Z_DEEP, Z_DEEP - 0.22], ORIG_BOT),
            color=PALETTE["ink_primary"], lw=0.70, ls=":", zorder=19)
    ax.plot(*proj_at([XC_R, XC_R], [0, 0], [Z_DEEP, Z_DEEP - 0.22], ORIG_BOT),
            color=PALETTE["ink_primary"], lw=0.70, ls=":", zorder=19)
    draw_2d_arrow(ax, p_cw_L, p_cw_R, color=PALETTE["ink_primary"], lw=1.15,
                  mutation_scale=8.0, arrowstyle="<|-|>", zorder=22)
    crisp_text(
        ax, 0.5 * (p_cw_L[0] + p_cw_R[0]), 0.5 * (p_cw_L[1] + p_cw_R[1]) - 0.10,
        r"Canal: $300\text{ m}$ ($h = 5\text{ m}$)",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_color=PALETTE["bed_front"], pad=0.02,
        fontsize=7.9, fontweight="bold", ha="center", va="top", zorder=25
    )

    # 2. Total Basin Width: 3000 m
    z_dim_w = Z_BASE - 0.34
    p_bw_0 = proj_at(0, 0, z_dim_w, ORIG_BOT)
    p_bw_1 = proj_at(WY, 0, z_dim_w, ORIG_BOT)
    ax.plot(*proj_at([0, 0], [0, 0], [Z_BASE, z_dim_w - 0.08], ORIG_BOT),
            color=PALETTE["ink_muted"], lw=0.70, ls=":", zorder=15)
    ax.plot(*proj_at([WY, WY], [0, 0], [Z_BASE, z_dim_w - 0.08], ORIG_BOT),
            color=PALETTE["ink_muted"], lw=0.70, ls=":", zorder=15)
    draw_2d_arrow(ax, p_bw_0, p_bw_1, color=PALETTE["ink_primary"], lw=1.15,
                  mutation_scale=8.5, arrowstyle="<|-|>", zorder=20)
    crisp_text(
        ax, 0.5 * (p_bw_0[0] + p_bw_1[0]) - 0.20, 0.5 * (p_bw_0[1] + p_bw_1[1]) - 0.14,
        r"Largura da bacia: $3000\text{ m}$ ($h_{\mathrm{rasa}} = 0{,}5\text{ m},\; 60\text{ células}$)",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_clear=True, pad=0.04,
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=25
    )

    # 3. Total Basin Length: 6000 m
    p_bl_0 = proj_at(WY, 0, z_dim_w, ORIG_BOT)
    p_bl_1 = proj_at(WY, LX, z_dim_w, ORIG_BOT)
    ax.plot(*proj_at([WY, WY], [LX, LX], [Z_BASE, z_dim_w - 0.08], ORIG_BOT),
            color=PALETTE["ink_muted"], lw=0.70, ls=":", zorder=15)
    draw_2d_arrow(ax, p_bl_0, p_bl_1, color=PALETTE["ink_primary"], lw=1.15,
                  mutation_scale=8.5, arrowstyle="<|-|>", zorder=20)
    crisp_text(
        ax, 0.5 * (p_bl_0[0] + p_bl_1[0]) + 0.22, 0.5 * (p_bl_0[1] + p_bl_1[1]) - 0.12,
        r"Comprimento da bacia: $6000\text{ m}$" + "\n" + r"($120\text{ células},\; \Delta x = \Delta y = 50\text{ m}$)",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_clear=True, pad=0.04,
        fontsize=8.2, fontweight="bold", ha="left", va="top", linespacing=1.18, zorder=25
    )

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-7.05, 10.45)
    ax.set_ylim(-8.35, 9.05)
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
