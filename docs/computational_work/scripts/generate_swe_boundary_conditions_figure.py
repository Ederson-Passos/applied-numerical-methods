"""
Ilustração científica vetorial (estilo Edward Tufte / monografia científica dos
anos 80 e 90) para a Seção 2.4.1 ("Identificação das fronteiras") das Equações
de Águas Rasas Bidimensionais (2D SWE) no domínio de Casulli (1990).

Combina a estética tridimensional sombreada e minimalista da Figura 1 com a
geometria da bacia com canal central e o arco solar de 12 h da Figura 9,
apresentando de forma precisa e conceitual:
  1. As 5 regiões de fronteira da tabela da Seção 2.4.1:
       - Oeste (x = 0), entrada do canal   -> Maré prescrita
       - Oeste (x = 0), restante da bacia  -> Parede impermeável
       - Leste (x = L_x)                   -> Parede impermeável
       - Sul   (y = 0)                     -> Parede impermeável
       - Norte (y = L_y)                   -> Parede impermeável
  2. A condição física e discreta de parede impermeável (u . n = 0):
     anulação exclusiva da componente normal (ex.: v = 0 em Norte/Sul e u = 0
     em Leste/Oeste fechado), preservando livre a componente tangencial
     (escorregamento livre / free-slip, sem impor artificialmente u = 0).
  3. Rosa dos ventos cartográfica projetada no plano (x, y) com Norte, Sul,
     Leste e Oeste alinhados exatamente às arestas da bacia.
  4. Deslocamento do sol no período semidiurno de 12 h (mesma arte da Figura 9).

Pode ser executado via terminal ou chamado no notebook `implementation.ipynb`:
    from generate_swe_boundary_conditions_figure import plot_boundary_identification
    plot_boundary_identification()

Salva/sobrescreve automaticamente em `../figures/`:
  - swe_boundary_conditions.svg
  - swe_boundary_conditions.pdf
  - swe_boundary_conditions.png
"""

import glob
import logging
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Polygon, FancyArrowPatch, Circle
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as pe

# Silencia avisos internos do fontTools sobre tabelas OpenType do MiKTeX
logging.getLogger("fontTools").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# 1. Tipografia LaTeX (Latin Modern Roman + Computer Modern Math)
# ---------------------------------------------------------------------------
for _fp in glob.glob(r"C:\Program Files\MiKTeX*\fonts\opentype\public\lm\lmroman*.otf"):
    fm.fontManager.addfont(_fp)
_HAS_LM = any(f.name == "Latin Modern Roman" for f in fm.fontManager.ttflist)

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

# ---------------------------------------------------------------------------
# 2. Paleta Editorial Idêntica às Figuras 1 e 9
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FCFBF7",       # Papel marfim/creme da Figura 1
    "ink_primary": "#11161C",     # Nanquim profundo para títulos e matemática
    "ink_secondary": "#222B35",   # Carvão nítido para textos explicativos
    "ink_muted": "#687380",       # Cinza-ardósia para linhas-guia curvas
    "rule_dark": "#283648",       # Plano de referência não perturbado eta = 0
    "navy_deep": "#0D3149",       # Azul-prussiano (vetores tangenciais e títulos)
    "z_node": "#145374",          # Azul-cerúleo (fronteira aberta / maré prescrita)
    "teal_open": "#17575A",       # Verde-petróleo (faces horizontais v e maré)
    "wall_red": "#8E321E",        # Terracota veneziano (parede impermeável / u_n = 0)
    "amber_sun": "#A86518",       # Âmbar solar de 12 h (idêntico à Figura 9)
    "water_front": "#A9CCE0",     # Face frontal da água (idêntica à Figura 1)
    "water_right": "#8EB8D1",     # Face lateral direita da água (idêntica à Figura 1)
    "water_chan": "#5B92B5",      # Água profunda na boca do canal (idêntica à Figura 9)
    "water_edge": "#204B69",      # Aresta estrutural da água
    "water_mesh": "#4A7C9B",      # Isolinhas suaves da superfície livre
    "bed_top": "#DFD5C7",         # Topo da planície rasa (h = 0,5 m)
    "bed_chan_top": "#9E8D7B",    # Fundo do canal central (h = 5,0 m)
    "bed_chan_wall": "#B5A695",   # Parede interna do degrau do canal
    "bed_front": "#C8BBAE",       # Corte geológico esquerdo (Oeste, x = 0)
    "bed_right": "#B3A494",       # Corte geológico direito (Sul, y = 0)
    "bed_edge": "#5E4F41",        # Contorno do leito
    "bed_hatch": "#827161",       # Hachuras sedimentares da Figura 1
}


def crisp_text(
    ax, x, y, s, color="#11161C", stroke_w=0.16, bg_pill=None, pad=0.08,
    border_col="none", border_lw=0.0, alpha_bg=0.90, **kwargs
):
    """Renderiza tipografia LaTeX nítida com micro-reforço vetorial sem halo."""
    if bg_pill is not None:
        kwargs["bbox"] = dict(
            boxstyle=f"square,pad={pad}",
            facecolor=bg_pill,
            edgecolor=border_col,
            linewidth=border_lw,
            alpha=alpha_bg,
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
    """Ícone vetorial astronômico do sol de 12 raios (idêntico à Figura 9)."""
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


def add_tufte_callout(
    ax, target_2d, box_pos_2d, leader_start_2d, title_str, lines_list,
    title_color="#0D3149", align="left", rad=0.14, zorder=28
):
    """Bloco de chamada editorial sem caixa (idêntico à Figura 1)."""
    tx, ty = target_2d
    bx, by = box_pos_2d
    lx, ly = leader_start_2d

    ax.plot(tx, ty, marker="o", markersize=3.6, color=title_color, zorder=zorder)
    conn = FancyArrowPatch(
        (lx, ly), (tx, ty),
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-",
        color=PALETTE["ink_muted"],
        linewidth=0.80,
        zorder=zorder - 2,
    )
    ax.add_patch(conn)

    crisp_text(
        ax, bx, by, title_str,
        color=title_color, stroke_w=0.19,
        fontsize=9.15, fontweight="bold",
        ha=align, va="bottom", zorder=zorder + 1,
    )
    body_text = "\n".join(lines_list)
    crisp_text(
        ax, bx, by - 0.08, body_text,
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.35, ha=align, va="top",
        linespacing=1.30, zorder=zorder + 1,
    )


# ---------------------------------------------------------------------------
# 3. Projeção Axonométrica Destra (x: Oeste->Leste, y: Sul->Norte, z: Vertical)
#    Mantém exatamente a perspectiva da Figura 9 com a boca Oeste (x=0) visível
#    em corte frontal à esquerda e Sul (y=0) visível à frente/direita!
# ---------------------------------------------------------------------------
LX = 9.00          # Comprimento L_x = 6000 m (Oeste x=0 -> Leste x=L_x)
WY = 7.00          # Largura     L_y = 3000 m (Sul   y=0 -> Norte y=L_y)
YC_S = 2.62        # Borda sul do canal central (y = 1350 m)
YC_N = 4.38        # Borda norte do canal central (y = 1650 m)

Z_SHALLOW = -0.52  # Leito das planícies rasas (h = 0,5 m)
Z_DEEP = -1.32     # Leito do canal profundo   (h = 5,0 m)
Z_BASE = -1.92     # Base do bloco geológico

# Vetores de base projetados: det(EX_P, EY_P) > 0 (sistema 100% destro!)
_ANG_X = np.deg2rad(24.0)    # +x: Oeste -> Leste (sobe para a direita)
_ANG_Y = np.deg2rad(165.5)   # +y: Sul   -> Norte (sobe para a esquerda)
EX_P = np.array([0.63 * np.cos(_ANG_X), 0.63 * np.sin(_ANG_X)])
EY_P = np.array([0.95 * np.cos(_ANG_Y), 0.95 * np.sin(_ANG_Y)])
EZ_P = np.array([0.0, 1.00])

ORIG_BASIN = (1.55, -1.72)   # Canto Sudoeste (x = 0, y = 0, z = 0) — margens amplas à esq./dir.


def proj(x, y, z, orig=ORIG_BASIN):
    xa, ya, za = np.asarray(x), np.asarray(y), np.asarray(z)
    X = orig[0] + xa * EX_P[0] + ya * EY_P[0] + za * EZ_P[0]
    Y = orig[1] + xa * EX_P[1] + ya * EY_P[1] + za * EZ_P[1]
    return X, Y


def draw_3d_arrow(
    ax, p0, p1, color, lw=1.5, mutation_scale=11.0, arrowstyle="-|>",
    zorder=22, ls="-", alpha=1.0
):
    return draw_2d_arrow(
        ax, proj(*p0), proj(*p1), color=color, lw=lw,
        mutation_scale=mutation_scale, arrowstyle=arrowstyle,
        zorder=zorder, ls=ls, alpha=alpha
    )


def free_surface_eta(x, y):
    """
    Superfície livre ondulante suave inspirada na Figura 1:
    Maré prescrita entrando em x = 0 pelo canal central e propagando-se de
    Oeste para Leste com leve espalhamento transversal.
    """
    xa, ya = np.asarray(x), np.asarray(y)
    yc_mid = 0.5 * (YC_S + YC_N)
    r_lat = (ya - yc_mid) / (0.5 * WY)
    wave_main = 0.24 * np.cos(1.65 * np.pi * (xa / LX) - 0.30) * np.exp(-0.22 * (r_lat ** 2))
    wave_sec = 0.065 * np.sin(2.8 * np.pi * (xa / LX) + 0.7 * np.pi * r_lat)
    return 0.08 + wave_main + wave_sec


# ---------------------------------------------------------------------------
# 4. Rosa dos Ventos Cartográfica 3D (Alinhada aos Eixos Físicos x e y)
# ---------------------------------------------------------------------------
def draw_compass_rose_3d(ax, center_2d, scale=1.08, zorder=26):
    """
    Desenha uma rosa dos ventos clássica dos anos 80/90 projetada exatamente no
    plano horizontal (x, y) da bacia:
      +x = Leste,  -x = Oeste,  +y = Norte,  -y = Sul.
    """
    cx, cy = center_2d

    # Vetores unitários no plano horizontal projetado (normalizados visualmente
    # mantendo as direções exatas das arestas da bacia!)
    u_E = EX_P / np.linalg.norm(EX_P) * scale
    u_W = -u_E
    u_N = EY_P / np.linalg.norm(EY_P) * (1.06 * scale)
    u_S = -u_N

    # Anel elíptico externo de azimute no plano projetado
    th = np.linspace(0, 2 * np.pi, 160)
    ring_xy = (
        np.array([[cx], [cy]])
        + 0.76 * np.outer(u_E, np.cos(th))
        + 0.76 * np.outer(u_N, np.sin(th))
    )
    ax.plot(ring_xy[0], ring_xy[1], color=PALETTE["ink_muted"], lw=0.80, alpha=0.75, zorder=zorder - 2)
    ring_in = (
        np.array([[cx], [cy]])
        + 0.68 * np.outer(u_E, np.cos(th))
        + 0.68 * np.outer(u_N, np.sin(th))
    )
    ax.plot(ring_in[0], ring_in[1], color=PALETTE["bed_edge"], lw=0.45, ls=":", alpha=0.65, zorder=zorder - 2)

    # Pontas colaterais secundárias (NE, NW, SE, SW)
    for v_a, v_b in [(u_N, u_E), (u_N, u_W), (u_S, u_E), (u_S, u_W)]:
        tip = np.array([cx, cy]) + 0.46 * (v_a + v_b)
        side1 = np.array([cx, cy]) + 0.12 * v_a
        side2 = np.array([cx, cy]) + 0.12 * v_b
        ax.add_patch(Polygon(
            [(cx, cy), tuple(side1), tuple(tip)],
            closed=True, facecolor="#9AA6B2", edgecolor=PALETTE["ink_primary"], lw=0.45, zorder=zorder - 1
        ))
        ax.add_patch(Polygon(
            [(cx, cy), tuple(tip), tuple(side2)],
            closed=True, facecolor="#EFECE4", edgecolor=PALETTE["ink_primary"], lw=0.45, zorder=zorder - 1
        ))

    # 4 Pontas cardeais principais chanfradas (bicolor estilo carta náutica)
    cardinals = [
        (u_N, 0.17 * u_E, -0.17 * u_E, PALETTE["wall_red"], "#F2DFD7"),   # Norte destacado em terracota
        (u_S, -0.17 * u_E, 0.17 * u_E, PALETTE["navy_deep"], "#E6DEC8"),  # Sul
        (u_E, -0.17 * u_N, 0.17 * u_N, PALETTE["navy_deep"], "#E6DEC8"),  # Leste
        (u_W, 0.17 * u_N, -0.17 * u_N, PALETTE["navy_deep"], "#E6DEC8"),  # Oeste
    ]
    c_pt = np.array([cx, cy])
    for v_main, v_left, v_right, col_dark, col_light in cardinals:
        tip = c_pt + v_main
        p_l = c_pt + v_left
        p_r = c_pt + v_right
        ax.add_patch(Polygon(
            [tuple(c_pt), tuple(p_l), tuple(tip)],
            closed=True, facecolor=col_dark, edgecolor=PALETTE["ink_primary"], lw=0.65, zorder=zorder
        ))
        ax.add_patch(Polygon(
            [tuple(c_pt), tuple(tip), tuple(p_r)],
            closed=True, facecolor=col_light, edgecolor=PALETTE["ink_primary"], lw=0.65, zorder=zorder
        ))

    ax.add_patch(Circle(
        (cx, cy), 0.055 * scale,
        facecolor="#FCFBF7", edgecolor=PALETTE["ink_primary"], lw=0.85, zorder=zorder + 1
    ))

    # Rótulos cardeais com as coordenadas exatas mencionadas na Seção 2.4.1
    pN = c_pt + 1.16 * u_N
    pS = c_pt + 1.16 * u_S
    pE = c_pt + 1.16 * u_E
    pW = c_pt + 1.16 * u_W

    crisp_text(ax, pN[0] - 0.04, pN[1] + 0.04, "Norte\n" + r"($y = L_y$)",
               color=PALETTE["wall_red"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.3, fontweight="bold", ha="right", va="bottom", linespacing=1.10, zorder=zorder + 2)
    crisp_text(ax, pS[0] + 0.04, pS[1] - 0.04, "Sul\n" + r"($y = 0$)",
               color=PALETTE["navy_deep"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.3, fontweight="bold", ha="left", va="top", linespacing=1.10, zorder=zorder + 2)
    crisp_text(ax, pE[0] + 0.06, pE[1] + 0.03, "Leste\n" + r"($x = L_x$)",
               color=PALETTE["navy_deep"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.3, fontweight="bold", ha="left", va="bottom", linespacing=1.10, zorder=zorder + 2)
    crisp_text(ax, pW[0] - 0.06, pW[1] - 0.03, "Oeste\n" + r"($x = 0$)",
               color=PALETTE["z_node"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.3, fontweight="bold", ha="right", va="top", linespacing=1.10, zorder=zorder + 2)


# ---------------------------------------------------------------------------
# 5. Auxiliar para Vetores Normal (Anulado) vs. Tangencial (Livre) nas Paredes
# ---------------------------------------------------------------------------
def draw_wall_bc_vectors(
    ax, p_wall_3d, vec_normal_3d, vec_tang_3d,
    lbl_normal, lbl_tang, lbl_n_vec=None,
    n_off=(0.0, 0.0), norm_off=(0.0, 0.0), tang_off=(0.0, 0.0),
    marker_face="s", marker_col="#8E321E", zorder=23
):
    """
    Ilustra localmente na face da malha escalonada:
      - O vetor unitário normal exterior n
      - A componente normal anulada (seta tracejada terracota com 'x' -> 0)
      - A componente tangencial livre (seta azul-prussiano sólida paralela à borda)
    """
    pw = np.asarray(p_wall_3d, dtype=float)
    vn = np.asarray(vec_normal_3d, dtype=float)
    vt = np.asarray(vec_tang_3d, dtype=float)

    pw_2d = proj(*pw)
    ax.plot(pw_2d[0], pw_2d[1], marker=marker_face, markersize=6.0,
            markerfacecolor=marker_col, markeredgecolor="white",
            markeredgewidth=0.95, zorder=zorder + 2)

    # 1) Vetor normal unitário exterior n (cinza-ardósia escuro)
    p_n_end = pw + vn
    draw_3d_arrow(ax, pw, p_n_end, color=PALETTE["ink_primary"],
                  lw=1.35, mutation_scale=9.5, zorder=zorder)
    if lbl_n_vec is not None:
        pn2 = proj(*p_n_end)
        crisp_text(ax, pn2[0] + n_off[0], pn2[1] + n_off[1], lbl_n_vec,
                   color=PALETTE["ink_primary"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.03,
                   fontsize=8.3, fontweight="bold", ha="center", va="center", zorder=zorder + 3)

    # 2) Componente normal bloqueada/anulada (tracejada com X sobreposto)
    p_vn_start = pw - 0.15 * vn
    p_vn_end = pw + 0.62 * vn
    draw_3d_arrow(ax, p_vn_start, p_vn_end, color=PALETTE["wall_red"],
                  lw=1.55, mutation_scale=9.5, ls="--", zorder=zorder + 1)
    pm_x = proj(*(pw + 0.30 * vn))
    ax.plot(pm_x[0], pm_x[1], marker="x", markersize=7.2,
            markeredgecolor=PALETTE["wall_red"], markeredgewidth=2.0, zorder=zorder + 3)
    if lbl_normal:
        crisp_text(ax, pm_x[0] + norm_off[0], pm_x[1] + norm_off[1], lbl_normal,
                   color=PALETTE["wall_red"], stroke_w=0.16, bg_pill="#F9EFEA", pad=0.04,
                   fontsize=8.1, fontweight="bold", ha="center", va="center", zorder=zorder + 3)

    # 3) Componente tangencial livre (paralela à parede, sem bloqueio!)
    p_vt_start = pw - 0.45 * vt
    p_vt_end = pw + 0.85 * vt
    draw_3d_arrow(ax, p_vt_start, p_vt_end, color=PALETTE["navy_deep"],
                  lw=2.15, mutation_scale=11.5, zorder=zorder + 1)
    if lbl_tang:
        pt2 = proj(*(pw + 0.45 * vt))
        crisp_text(ax, pt2[0] + tang_off[0], pt2[1] + tang_off[1], lbl_tang,
                   color=PALETTE["navy_deep"], stroke_w=0.16, bg_pill="#E4F0F7", pad=0.04,
                   fontsize=8.1, fontweight="bold", ha="center", va="center", zorder=zorder + 3)


# ---------------------------------------------------------------------------
# 6. Construção Completa da Prancha Conceitual da Seção 2.4.1
# ---------------------------------------------------------------------------
def plot_boundary_identification(
    output_stem="swe_boundary_conditions",
    save_formats=("svg", "pdf", "png"),
    show=True,
    return_paths=False,
):
    rc_vintage = {
        "font.family": "Latin Modern Roman" if _HAS_LM else "serif",
        "mathtext.fontset": "cm",
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "axes.unicode_minus": True,
        "figure.facecolor": PALETTE["bg_canvas"],
        "savefig.facecolor": PALETTE["bg_canvas"],
    }

    with plt.rc_context(rc_vintage):
        fig, ax = plt.subplots(figsize=(16.0, 9.5), dpi=300)
        fig.patch.set_facecolor(PALETTE["bg_canvas"])
        ax.set_facecolor(PALETTE["bg_canvas"])

        # ===================================================================
        # CAMADA 0: ARCO SOLAR DE 12 HORAS NO TOPO (MESMA ARTE DA FIGURA 9)
        # ===================================================================
        x_sun_L, y_sun_L = -5.65, 3.88
        x_sun_M, y_sun_M = 0.15, 5.15
        x_sun_R, y_sun_R = 5.95, 3.88

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
            sn = s_arr + 0.022
            pb = (1 - sn) ** 2 * P0_s + 2 * (1 - sn) * sn * P1_s + (sn ** 2) * P2_s
            draw_2d_arrow(ax, tuple(pa), tuple(pb), color=PALETTE["amber_sun"],
                          lw=1.35, mutation_scale=9.0, zorder=20)

        draw_stylized_sun(ax, x_sun_L, y_sun_L, color=PALETTE["amber_sun"])
        crisp_text(ax, x_sun_L, y_sun_L - 0.28, r"$t = 0\,\mathrm{h}$",
                   color=PALETTE["amber_sun"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.03,
                   fontsize=8.2, fontweight="bold", ha="center", va="top", zorder=26)

        draw_stylized_sun(ax, x_sun_M, y_sun_M, color=PALETTE["amber_sun"])
        crisp_text(ax, x_sun_M, y_sun_M + 0.28, r"$t = 6\,\mathrm{h}$",
                   color=PALETTE["amber_sun"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.03,
                   fontsize=8.3, fontweight="bold", ha="center", va="bottom", zorder=26)

        draw_stylized_sun(ax, x_sun_R, y_sun_R, color=PALETTE["amber_sun"])
        crisp_text(ax, x_sun_R, y_sun_R - 0.28, r"$t = 12\,\mathrm{h}$",
                   color=PALETTE["amber_sun"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.03,
                   fontsize=8.2, fontweight="bold", ha="center", va="top", zorder=26)

        crisp_text(
            ax, x_sun_M, y_sun_M - 0.34,
            r"Deslocamento Solar de $12\,\mathrm{h}$ (Ciclo Semidiurno $M_2$) — governa a maré prescrita na entrada do canal ($x = 0$)",
            color=PALETTE["amber_sun"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.05,
            fontsize=8.55, fontweight="bold", fontstyle="italic", ha="center", va="top", zorder=26
        )

        # ===================================================================
        # CAMADA 1: BACIA 3D COM CANAL CENTRAL (ESTÉTICA SOMBREADA DA FIG. 1)
        # ===================================================================
        nx, ny = 64, 52
        xg = np.linspace(0, LX, nx)
        yg = np.linspace(0, WY, ny)
        XX, YY = np.meshgrid(xg, yg, indexing="ij")
        ZZ = free_surface_eta(XX, YY)

        # 1.1 Leito submerso (planícies laterais h = 0,5 m e canal central h = 5,0 m)
        for (ya, yb) in [(0.0, YC_S), (YC_N, WY)]:
            pts_sh = [
                proj(0, ya, Z_SHALLOW), proj(LX, ya, Z_SHALLOW),
                proj(LX, yb, Z_SHALLOW), proj(0, yb, Z_SHALLOW),
            ]
            ax.add_patch(Polygon(
                pts_sh, closed=True, facecolor=PALETTE["bed_top"],
                edgecolor=PALETTE["bed_edge"], lw=0.70, alpha=0.94, zorder=3
            ))

        # Parede vertical interna visível do degrau do canal (em y = YC_N)
        pts_cwall = [
            proj(0, YC_N, Z_DEEP), proj(LX, YC_N, Z_DEEP),
            proj(LX, YC_N, Z_SHALLOW), proj(0, YC_N, Z_SHALLOW),
        ]
        ax.add_patch(Polygon(
            pts_cwall, closed=True, facecolor=PALETTE["bed_chan_wall"],
            edgecolor=PALETTE["bed_edge"], lw=0.75, alpha=0.95, zorder=3.4
        ))

        # Piso do canal central profundo (y in [YC_S, YC_N])
        pts_cfloor = [
            proj(0, YC_S, Z_DEEP), proj(LX, YC_S, Z_DEEP),
            proj(LX, YC_N, Z_DEEP), proj(0, YC_N, Z_DEEP),
        ]
        ax.add_patch(Polygon(
            pts_cfloor, closed=True, facecolor=PALETTE["bed_chan_top"],
            edgecolor=PALETTE["bed_edge"], lw=0.80, alpha=0.95, zorder=3.8
        ))

        # Arestas verticais traseiras sutis (canto Nordeste x=LX, y=WY)
        ax.plot(*proj([LX, LX], [WY, WY], [Z_SHALLOW, float(free_surface_eta(LX, WY))]),
                color=PALETTE["ink_muted"], lw=0.65, ls=":", alpha=0.55, zorder=5)

        # 1.2 Cortes Geológicos Frontais com Hachuras Triplas da Figura 1
        # Face Frontal-Esquerda: Fronteira Oeste (x = 0, com degrau do canal!)
        stepped_west_3d = [
            (0, 0, Z_SHALLOW),
            (0, YC_S, Z_SHALLOW),
            (0, YC_S, Z_DEEP),
            (0, YC_N, Z_DEEP),
            (0, YC_N, Z_SHALLOW),
            (0, WY, Z_SHALLOW),
            (0, WY, Z_BASE),
            (0, 0, Z_BASE),
        ]
        ax.add_patch(Polygon(
            [proj(*p) for p in stepped_west_3d], closed=True,
            facecolor=PALETTE["bed_front"], edgecolor=PALETTE["bed_edge"],
            lw=1.05, alpha=0.97, zorder=12
        ))

        def west_bed_z(yv):
            return Z_DEEP if (YC_S < yv < YC_N) else Z_SHALLOW

        for yh in np.linspace(0.22, WY - 0.22, 34):
            for k_sub in range(3):
                y_s = np.clip(yh + (k_sub - 1) * 0.05, 0.08, WY - 0.08)
                if abs(y_s - YC_S) < 0.12 or abs(y_s - YC_N) < 0.12:
                    continue
                zt = west_bed_z(y_s)
                zb = max(Z_BASE + 0.06, zt - 0.26 + 0.04 * k_sub)
                ax.plot(*proj([0, 0], [y_s, y_s - 0.12], [zt, zb]),
                        color=PALETTE["bed_hatch"], lw=0.48, alpha=0.68, zorder=12.5)

        # Face Frontal-Direita: Fronteira Sul (y = 0, de x=0 até x=LX)
        pts_south_bed = [
            proj(0, 0, Z_SHALLOW), proj(LX, 0, Z_SHALLOW),
            proj(LX, 0, Z_BASE), proj(0, 0, Z_BASE),
        ]
        ax.add_patch(Polygon(
            pts_south_bed, closed=True,
            facecolor=PALETTE["bed_right"], edgecolor=PALETTE["bed_edge"],
            lw=1.00, alpha=0.97, zorder=12
        ))
        for xh in np.linspace(0.28, LX - 0.28, 32):
            for k_sub in range(3):
                x_s = np.clip(xh + (k_sub - 1) * 0.06, 0.08, LX - 0.08)
                ax.plot(*proj([x_s, x_s - 0.14], [0, 0], [Z_SHALLOW, Z_SHALLOW - 0.27 + 0.04 * k_sub]),
                        color="#736354", lw=0.48, alpha=0.66, zorder=12.5)

        # 1.3 Faces Verticais Translúcidas da Coluna d'Água (Oeste x=0 e Sul y=0)
        yg_s1 = np.linspace(0, YC_S, 20)
        yg_s2 = np.linspace(YC_N, WY, 20)
        yg_ch = np.linspace(YC_S, YC_N, 20)

        for y_seg in [yg_s1, yg_s2]:
            pts_w = (
                [proj(0, y_, free_surface_eta(0, y_)) for y_ in y_seg]
                + [proj(0, y_seg[-1], Z_SHALLOW), proj(0, y_seg[0], Z_SHALLOW)]
            )
            ax.add_patch(Polygon(
                pts_w, closed=True, facecolor=PALETTE["water_front"],
                edgecolor="none", alpha=0.46, zorder=13
            ))

        pts_w_ch = (
            [proj(0, y_, free_surface_eta(0, y_)) for y_ in yg_ch]
            + [proj(0, YC_N, Z_DEEP), proj(0, YC_S, Z_DEEP)]
        )
        ax.add_patch(Polygon(
            pts_w_ch, closed=True, facecolor=PALETTE["water_chan"],
            edgecolor="none", alpha=0.62, zorder=13.2
        ))

        pts_w_south = (
            [proj(x_, 0, free_surface_eta(x_, 0)) for x_ in xg]
            + [proj(LX, 0, Z_SHALLOW), proj(0, 0, Z_SHALLOW)]
        )
        ax.add_patch(Polygon(
            pts_w_south, closed=True, facecolor=PALETTE["water_right"],
            edgecolor="none", alpha=0.44, zorder=13
        ))

        # 1.4 Superfície Livre Sombreada 3D com Malha Fina (Arte da Figura 1!)
        shelf_cmap = LinearSegmentedColormap.from_list("fig1_shelf", ["#7FAAC6", "#B3D2E5", "#E8F3FA"])
        chan_cmap = LinearSegmentedColormap.from_list("fig1_chan", ["#4B80A3", "#74A5C5", "#B5D6EA"])
        z_s_min, z_s_max = ZZ.min(), ZZ.max()

        for i in range(nx - 1):
            for j in range(ny - 1):
                xs = [XX[i, j], XX[i + 1, j], XX[i + 1, j + 1], XX[i, j + 1]]
                ys = [YY[i, j], YY[i + 1, j], YY[i + 1, j + 1], YY[i, j + 1]]
                zs = [ZZ[i, j], ZZ[i + 1, j], ZZ[i + 1, j + 1], ZZ[i, j + 1]]
                X2, Y2 = proj(xs, ys, zs)
                y_m = 0.25 * sum(ys)
                z_m = 0.25 * sum(zs)
                in_chan = (YC_S <= y_m <= YC_N)
                norm_z = (z_m - z_s_min) / (z_s_max - z_s_min + 1e-9)
                dz_dx = (ZZ[i + 1, j] - ZZ[i, j]) / (xg[1] - xg[0])
                light = np.clip(0.60 * norm_z + 0.30 - 0.30 * dz_dx, 0.06, 0.96)
                col = chan_cmap(light) if in_chan else shelf_cmap(light)
                ax.add_patch(Polygon(
                    list(zip(X2, Y2)), facecolor=col, edgecolor=col,
                    lw=0.10, alpha=0.80 if in_chan else 0.74, zorder=15
                ))

        for i in range(0, nx, 4):
            ax.plot(*proj(XX[i, :], YY[i, :], ZZ[i, :]),
                    color=PALETTE["water_mesh"], lw=0.38, alpha=0.48, zorder=15.5)
        for j in range(0, ny, 4):
            ax.plot(*proj(XX[:, j], YY[:, j], ZZ[:, j]),
                    color=PALETTE["water_mesh"], lw=0.38, alpha=0.48, zorder=15.5)

        # Linhas tracejadas das margens internas do canal central (y = 1350 m e y = 1650 m)
        for y_ch_b in (YC_S, YC_N):
            ax.plot(*proj(xg, np.full(nx, y_ch_b), free_surface_eta(xg, y_ch_b)),
                    color=PALETTE["navy_deep"], lw=0.95, ls=(0, (5, 3)), alpha=0.75, zorder=16)

        # Nível de referência não perturbado eta = 0 nas faces frontais
        ax.plot(*proj(np.zeros(ny), yg, np.zeros(ny)),
                color=PALETTE["rule_dark"], lw=1.00, ls=(0, (5, 3)), zorder=16.5)
        ax.plot(*proj(xg, np.zeros(nx), np.zeros(nx)),
                color=PALETTE["rule_dark"], lw=1.00, ls=(0, (5, 3)), zorder=16.5)

        # Arestas estruturais verticais do bloco
        for (xe, ye), lwe in [((0, 0), 1.35), ((0, WY), 1.15), ((LX, 0), 1.25)]:
            ax.plot(*proj([xe, xe], [ye, ye], [Z_BASE, float(free_surface_eta(xe, ye))]),
                    color=PALETTE["water_edge"], lw=lwe, zorder=17)

        # ===================================================================
        # CAMADA 2: DEMARCAÇÃO VISUAL DAS 5 FRONTEIRAS (PAREDES VS. ABERTA)
        # ===================================================================
        # 2.1 Paredes Impermeáveis (contorno terracota espesso + hachura externa de muro rígido)
        #   a) Norte (y = WY, x in [0, LX])
        ax.plot(*proj(xg, np.full(nx, WY), free_surface_eta(xg, WY)),
                color=PALETTE["wall_red"], lw=2.35, zorder=18)
        for x_ht in np.linspace(0.45, LX - 0.45, 16):
            zh = float(free_surface_eta(x_ht, WY))
            ax.plot(*proj([x_ht, x_ht - 0.18], [WY, WY + 0.22], [zh, zh + 0.03]),
                    color=PALETTE["wall_red"], lw=0.75, alpha=0.80, zorder=18)

        #   b) Leste (x = LX, y in [0, WY])
        ax.plot(*proj(np.full(ny, LX), yg, free_surface_eta(LX, yg)),
                color=PALETTE["wall_red"], lw=2.35, zorder=18)
        for y_ht in np.linspace(0.40, WY - 0.40, 13):
            zh = float(free_surface_eta(LX, y_ht))
            ax.plot(*proj([LX, LX + 0.24], [y_ht, y_ht + 0.14], [zh, zh + 0.03]),
                    color=PALETTE["wall_red"], lw=0.75, alpha=0.80, zorder=18)

        #   c) Sul (y = 0, x in [0, LX])
        ax.plot(*proj(xg, np.zeros(nx), free_surface_eta(xg, 0)),
                color=PALETTE["wall_red"], lw=2.45, zorder=18.5)
        for x_ht in np.linspace(0.45, LX - 0.45, 16):
            zh = float(free_surface_eta(x_ht, 0))
            ax.plot(*proj([x_ht, x_ht + 0.16], [0, -0.20], [zh, zh - 0.02]),
                    color=PALETTE["wall_red"], lw=0.75, alpha=0.80, zorder=18.5)

        #   d) Oeste — restante da bacia (x = 0, y in [0, YC_S] e y in [YC_N, WY])
        for y_seg in [yg_s1, yg_s2]:
            ax.plot(*proj(np.zeros_like(y_seg), y_seg, free_surface_eta(0, y_seg)),
                    color=PALETTE["wall_red"], lw=2.55, zorder=19)
        for y_ht in np.concatenate([np.linspace(0.30, YC_S - 0.25, 6),
                                    np.linspace(YC_N + 0.25, WY - 0.30, 6)]):
            zh = float(free_surface_eta(0, y_ht))
            ax.plot(*proj([0, -0.24], [y_ht, y_ht - 0.12], [zh, zh - 0.02]),
                    color=PALETTE["wall_red"], lw=0.80, alpha=0.82, zorder=19)

        # 2.2 Fronteira Aberta: Oeste (x = 0), entrada do canal (y in [YC_S, YC_N])
        ax.plot(*proj(np.zeros_like(yg_ch), yg_ch, free_surface_eta(0, yg_ch)),
                color=PALETTE["amber_sun"], lw=3.40, solid_capstyle="butt", zorder=20)
        # Portal vertical da boca aberta do canal
        for y_p in (YC_S, YC_N):
            ax.plot(*proj([0, 0], [y_p, y_p], [Z_DEEP, float(free_surface_eta(0, y_p))]),
                    color=PALETTE["z_node"], lw=1.60, zorder=19.5)

        # Setas bidirecionais da maré prescrita na entrada aberta do canal
        yc_mouth = 0.5 * (YC_S + YC_N)
        zm_mouth = -0.35
        draw_3d_arrow(ax, (-1.05, yc_mouth, zm_mouth), (0.95, yc_mouth, zm_mouth),
                      color=PALETTE["z_node"], lw=2.45, mutation_scale=13.0,
                      arrowstyle="<|-|>", zorder=22)

        # ===================================================================
        # CAMADA 3: DECOMPOSIÇÃO u . n = 0 NAS 4 PAREDES IMPERMEÁVEIS
        #           (Componente normal = 0 vs. Componente tangencial livre!)
        # ===================================================================
        # 1) Fronteira Sul (y = 0, face horizontal '^'): n = (0, -1) => v = 0, mas u != 0 livre!
        xs_bc = 4.85
        zs_bc = float(free_surface_eta(xs_bc, 0)) + 0.03
        draw_wall_bc_vectors(
            ax,
            p_wall_3d=(xs_bc, 0.0, zs_bc),
            vec_normal_3d=(0.0, -1.18, 0.0),
            vec_tang_3d=(1.30, 0.0, 0.0),
            lbl_normal=r"$v = 0$ (normal)",
            lbl_tang=r"$u \neq 0$ (tangencial livre)",
            lbl_n_vec=r"$\mathbf{n} = (0, -1)$",
            n_off=(0.56, -0.06),
            norm_off=(0.68, 0.14),
            tang_off=(-0.18, 0.26),
            marker_face="^",
            marker_col=PALETTE["teal_open"],
            zorder=23,
        )

        # 2) Fronteira Norte (y = L_y, face horizontal '^'): n = (0, +1) => v = 0, mas u != 0 livre!
        xn_bc = 4.90
        zn_bc = float(free_surface_eta(xn_bc, WY)) + 0.03
        draw_wall_bc_vectors(
            ax,
            p_wall_3d=(xn_bc, WY, zn_bc),
            vec_normal_3d=(0.0, 1.00, 0.0),
            vec_tang_3d=(1.22, 0.0, 0.0),
            lbl_normal=r"$v = 0$",
            lbl_tang=r"$u \neq 0$ livre",
            lbl_n_vec=r"$\mathbf{n} = (0, +1)$",
            n_off=(-0.48, 0.12),
            norm_off=(0.34, 0.16),
            tang_off=(0.18, -0.22),
            marker_face="^",
            marker_col=PALETTE["teal_open"],
            zorder=23,
        )

        # 3) Fronteira Leste (x = L_x, face vertical 's'): n = (+1, 0) => u = 0, mas v != 0 livre!
        ye_bc = 3.55
        ze_bc = float(free_surface_eta(LX, ye_bc)) + 0.03
        draw_wall_bc_vectors(
            ax,
            p_wall_3d=(LX, ye_bc, ze_bc),
            vec_normal_3d=(1.20, 0.0, 0.0),
            vec_tang_3d=(0.0, 1.08, 0.0),
            lbl_normal=r"$u = 0$",
            lbl_tang=r"$v \neq 0$ livre",
            lbl_n_vec=r"$\mathbf{n} = (+1, 0)$",
            n_off=(0.52, 0.08),
            norm_off=(0.08, 0.24),
            tang_off=(-0.46, 0.18),
            marker_face="s",
            marker_col=PALETTE["wall_red"],
            zorder=23,
        )

        # 4) Fronteira Oeste fechada (x = 0, restante da bacia, face vertical 's'): n = (-1, 0) => u = 0, v != 0
        yw_bc = 1.25
        zw_bc = float(free_surface_eta(0.0, yw_bc)) + 0.03
        draw_wall_bc_vectors(
            ax,
            p_wall_3d=(0.0, yw_bc, zw_bc),
            vec_normal_3d=(-1.15, 0.0, 0.0),
            vec_tang_3d=(0.0, 0.92, 0.0),
            lbl_normal=r"$u = 0$",
            lbl_tang=r"$v \neq 0$",
            lbl_n_vec=r"$\mathbf{n} = (-1, 0)$",
            n_off=(-0.48, -0.14),
            norm_off=(-0.36, 0.16),
            tang_off=(0.34, 0.12),
            marker_face="s",
            marker_col=PALETTE["wall_red"],
            zorder=23,
        )

        # ===================================================================
        # CAMADA 4: OS 5 BLOCOS CONCEITUAIS (FIÉIS À TABELA DA SEÇÃO 2.4.1)
        #           Totalmente posicionados nas margens livres (zero sobreposição!)
        # ===================================================================
        # 1. Norte (y = L_y) -> Parede impermeável (canto superior esquerdo)
        p_t_north = proj(2.35, WY, float(free_surface_eta(2.35, WY)))
        add_tufte_callout(
            ax,
            target_2d=p_t_north,
            box_pos_2d=(-8.45, 2.72),
            leader_start_2d=(-4.40, 2.38),
            title_str=r"Fronteira Norte ($y = L_y$) — Parede Impermeável",
            lines_list=[
                r"Condição $\mathbf{u}\cdot\mathbf{n} = 0$ com $\mathbf{n} = (0, +1)$:",
                r"anula a componente normal $v = 0$ na face horizontal,",
                r"mantendo $u$ livre ao longo da margem.",
            ],
            title_color=PALETTE["wall_red"],
            align="left",
            rad=-0.12,
        )

        # 2. Leste (x = L_x) -> Parede impermeável (canto superior direito)
        p_t_east = proj(LX, 5.55, float(free_surface_eta(LX, 5.55)))
        add_tufte_callout(
            ax,
            target_2d=p_t_east,
            box_pos_2d=(3.55, 3.02),
            leader_start_2d=(3.42, 2.78),
            title_str=r"Fronteira Leste ($x = L_x$) — Parede Impermeável",
            lines_list=[
                r"Cabeceira fechada com $\mathbf{n} = (+1, 0)$:",
                r"impõe componente normal $u = 0$ na face vertical,",
                r"sem restringir a velocidade tangencial $v$.",
            ],
            title_color=PALETTE["wall_red"],
            align="left",
            rad=0.14,
        )

        # 3. Oeste (x = 0), restante da bacia -> Parede impermeável (aponta direto para a aba superior, sem cruzar!)
        p_t_west_sh = proj(0.0, 5.85, float(free_surface_eta(0.0, 5.85)))
        add_tufte_callout(
            ax,
            target_2d=p_t_west_sh,
            box_pos_2d=(-9.48, 1.18),
            leader_start_2d=(-5.32, 0.72),
            title_str=r"Oeste ($x = 0$), Restante da Bacia — Parede Impermeável",
            lines_list=[
                r"Trechos rasos fora do canal ($h = 0{,}5\,\mathrm{m}$, $\mathbf{n} = (-1, 0)$):",
                r"anula a componente normal $u = 0$ nas abas laterais,",
                r"preservando $v$ tangencial livre.",
            ],
            title_color=PALETTE["wall_red"],
            align="left",
            rad=-0.12,
        )

        # 4. Oeste (x = 0), entrada do canal -> Maré prescrita (aponta direto para a boca aberta, zero cruzamento!)
        p_t_mouth = proj(0.0, yc_mouth, -0.18)
        add_tufte_callout(
            ax,
            target_2d=p_t_mouth,
            box_pos_2d=(-9.48, -0.55),
            leader_start_2d=(-5.38, -0.96),
            title_str=r"Oeste ($x = 0$), Entrada do Canal — Maré Prescrita",
            lines_list=[
                r"Fronteira aberta ($y \in [1350, 1650]\,\mathrm{m}$, $h = 5{,}0\,\mathrm{m}$):",
                r"elevação imposta $\eta(0, y, t) = A\sin(2\pi t / T)$,",
                r"com $A = 0{,}4\,\mathrm{m}$ e período semidiurno $T = 12\,\mathrm{h}$.",
            ],
            title_color=PALETTE["z_node"],
            align="left",
            rad=0.14,
        )

        # 5. Sul (y = 0) + Escorregamento Livre (abaixo da face rochosa direita, em papel limpo!)
        p_t_south = proj(2.75, 0.0, float(free_surface_eta(2.75, 0.0)))
        add_tufte_callout(
            ax,
            target_2d=p_t_south,
            box_pos_2d=(4.05, -2.68),
            leader_start_2d=(3.95, -2.52),
            title_str=r"Fronteira Sul ($y = 0$) — Parede Impermeável ($\mathbf{u}\cdot\mathbf{n} = 0$)",
            lines_list=[
                r"Com $\mathbf{n} = (0, -1)$, anula-se apenas a componente normal ($v = 0$).",
                r"Escorregamento livre: não se impõe artificialmente $u = 0$",
                r"nas paredes Norte e Sul, respeitando a malha escalonada.",
            ],
            title_color=PALETTE["navy_deep"],
            align="left",
            rad=-0.14,
        )

        # Rótulos geométricos discretos no bloco geológico (livres das linhas-guia!)
        p_ch_lbl = proj(0.0, yc_mouth, Z_DEEP - 0.30)
        crisp_text(
            ax, p_ch_lbl[0] - 0.06, p_ch_lbl[1],
            r"Canal ($300\,\mathrm{m}$, $h = 5\,\mathrm{m}$)",
            color="#2E241B", stroke_w=0.14, bg_pill=PALETTE["bed_front"], pad=0.03,
            fontsize=7.75, fontweight="bold", ha="center", va="center", rotation=-14.5, zorder=22
        )
        p_lx_lbl = proj(0.42 * LX, 0.0, Z_BASE + 0.25)
        crisp_text(
            ax, p_lx_lbl[0], p_lx_lbl[1],
            r"$L_x = 6000\,\mathrm{m}$  ($x = 0 \longrightarrow L_x$)",
            color="#2E241B", stroke_w=0.14,
            fontsize=7.9, fontstyle="italic", ha="center", va="center", rotation=24.0, zorder=22
        )

        # ===================================================================
        # CAMADA 5: ROSA DOS VENTOS CARTOGRÁFICA 3D (MARGEM INFERIOR ESQUERDA LIVRE)
        # ===================================================================
        draw_compass_rose_3d(ax, center_2d=(-6.95, -2.95), scale=1.08, zorder=26)

        # Faixa-síntese booktabs no rodapé (bem abaixo do vértice inferior Y = -3.64 da bacia!)
        ax.plot([-9.45, 9.25], [-4.16, -4.16], color=PALETTE["ink_muted"], lw=0.75, alpha=0.55, zorder=10)
        crisp_text(
            ax, -0.10, -4.46,
            r"Síntese física e discreta da parede impermeável: $\;\mathbf{u}\cdot\mathbf{n} = u_n = 0\;$ "
            r"$\Longrightarrow$ bloqueia apenas o fluxo normal à fronteira ($u_n = 0$), preservando a velocidade tangencial $u_\tau$ livre",
            color=PALETTE["ink_primary"], stroke_w=0.16,
            fontsize=8.65, fontweight="bold", ha="center", va="center", zorder=27,
        )

        ax.set_xlim(-9.65, 9.45)
        ax.set_ylim(-4.82, 5.75)
        ax.set_aspect("equal")
        ax.axis("off")

        plt.tight_layout(pad=0.10)

        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        saved_paths = {}
        for fmt in save_formats:
            out_path = FIGURES_DIR / f"{output_stem}.{fmt}"
            save_kw = dict(
                format=fmt,
                bbox_inches="tight",
                facecolor=fig.get_facecolor(),
            )
            if fmt.lower() == "png":
                save_kw["dpi"] = 300
            fig.savefig(out_path, **save_kw)
            saved_paths[fmt] = out_path

        if show:
            plt.show()
        plt.close(fig)

    return saved_paths if return_paths else None


if __name__ == "__main__":
    paths = plot_boundary_identification(show=False, return_paths=True)
    for fmt_k, p_out in paths.items():
        print(f"Saved ({fmt_k}): {p_out}")
