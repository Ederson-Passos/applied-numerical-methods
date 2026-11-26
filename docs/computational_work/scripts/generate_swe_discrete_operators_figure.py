"""
Síntese visual editorial (estilo Edward Tufte / monografia científica dos anos
80 e 90) dos Operadores Discretos na Malha Escalonada de Casulli (Seção 2):
Gradiente da Superfície Livre, Divergência dos Fluxos Volumétricos, Contraste
Batimétrico (Planície Rasa vs. Canal Profundo) e Conservação Discreta por
Cancelamento Telescópico.

Pode ser executado diretamente via terminal ou chamado em célula do notebook
`implementation.ipynb`:
    from generate_swe_discrete_operators_figure import plot_discrete_operators_synthesis
    plot_discrete_operators_synthesis()

A cada execução, salva/sobrescreve automaticamente na pasta `../figures/`:
  - swe_discrete_operators.svg (vetorial com glifos convertidos em curvas)
  - swe_discrete_operators.pdf (vetorial para publicação LaTeX)
  - swe_discrete_operators.png (alta resolução 300 DPI)
"""

import glob
import logging
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch
import matplotlib.patheffects as pe

# Silencia avisos internos do fontTools sobre tabelas OpenType do MiKTeX
logging.getLogger("fontTools").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# 1. Registro da Tipografia LaTeX (Latin Modern Roman + Computer Modern Math)
# ---------------------------------------------------------------------------
for _fp in glob.glob(r"C:\Program Files\MiKTeX*\fonts\opentype\public\lm\lmroman*.otf"):
    fm.fontManager.addfont(_fp)
_HAS_LM = any(f.name == "Latin Modern Roman" for f in fm.fontManager.ttflist)

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

# ---------------------------------------------------------------------------
# 2. Paleta Cartográfica e Editorial Anos 80/90 (Idêntica às Figuras 1–10)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FCFBF7",       # Papel marfim/creme de arquivo
    "panel_card": "#FDFCFA",      # Fundo sutil para quadro esquemático
    "panel_tint": "#F5F1E9",      # Faixa editorial suave (booktabs)
    "ink_primary": "#11161C",     # Tinta nanquim profunda para títulos e matemática
    "ink_secondary": "#222B35",   # Carvão nítido para legendas explicativas
    "ink_muted": "#64707D",       # Cinza-ardósia para linhas de cota e guias
    "rule_light": "#D4CCC0",      # Fio divisório sutil
    "rule_dark": "#283648",       # Fio booktabs principal
    "navy_deep": "#0D3149",       # Azul-prussiano profundo (cabeçalhos)
    "z_node": "#145374",          # Azul-cerúleo (centros eta_{i,j} e subida)
    "u_node": "#8E321E",          # Terracota veneziano (faces verticais u / q_x / descida)
    "v_node": "#17575A",          # Verde-petróleo (faces horizontais v / q_y)
    "amber_acc": "#9C5E14",       # Âmbar seco (destaques de batimetria/transição)
    "water_body": "#C7E1F0",      # Corpo d'água translúcido (planície rasa)
    "water_deep": "#AED3E8",      # Água no canal profundo
    "water_front": "#B3D4E6",     # Face frontal 3D da coluna
    "water_right": "#97C0D8",     # Face lateral direita 3D da coluna
    "water_top": "#D6EAF5",       # Superfície livre 3D
    "water_edge": "#1E4966",      # Aresta estrutural da água
    "cell_bg": "#F3EFEA",         # Células vizinhas na malha 2D
    "cell_focus": "#E6F0F6",      # Célula central (i, j) em destaque
    "cell_border": "#4A5968",     # Arestas das células 2D
    "bed_top": "#D8CEC0",         # Topo do leito impermeável
    "bed_front": "#C8BBAE",       # Corte geológico frontal
    "bed_right": "#B3A494",       # Corte geológico lateral
    "bed_edge": "#5E4F41",        # Contorno do leito rochoso/sedimentar
    "bed_hatch": "#827161",       # Hachura geológica oblíqua estilo Tufte
}


def crisp_text(
    ax, x, y, s, color="#11161C", stroke_w=0.15, bg_pill=None, pad=0.10,
    border_col="none", border_lw=0.0, alpha_bg=0.92, **kwargs
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


def draw_arrow(
    ax, p0, p1, color, lw=1.35, mutation_scale=10.5, arrowstyle="-|>",
    zorder=20, ls="-", alpha=1.0, connectionstyle="arc3,rad=0.0"
):
    """Desenha seta vetorial precisa sem recuo nas extremidades."""
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


# ---------------------------------------------------------------------------
# 3. Projeção Axonométrica 3D (Idêntica a swe_continuity_meaning.py)
# ---------------------------------------------------------------------------
_ANGLE_X = np.deg2rad(-14.5)
_ANGLE_Y = np.deg2rad(28.0)
_EX = np.array([1.00 * np.cos(_ANGLE_X), 1.00 * np.sin(_ANGLE_X)])
_EY = np.array([0.64 * np.cos(_ANGLE_Y), 0.64 * np.sin(_ANGLE_Y)])
_EZ = np.array([0.0, 1.00])


def proj3d(x, y, z, origin=(0.0, 0.0)):
    x_a, y_a, z_a = np.asarray(x), np.asarray(y), np.asarray(z)
    X = origin[0] + x_a * _EX[0] + y_a * _EY[0] + z_a * _EZ[0]
    Y = origin[1] + x_a * _EX[1] + y_a * _EY[1] + z_a * _EZ[1]
    return X, Y


def draw_3d_arrow(
    ax, p_start, p_end, origin, color, lw=1.5, mutation_scale=11.0,
    arrowstyle="-|>", zorder=20, ls="-", alpha=1.0
):
    return draw_arrow(
        ax,
        proj3d(*p_start, origin=origin),
        proj3d(*p_end, origin=origin),
        color=color, lw=lw, mutation_scale=mutation_scale,
        arrowstyle=arrowstyle, zorder=zorder, ls=ls, alpha=alpha,
    )


# ---------------------------------------------------------------------------
# 4. Construção do Painel Esquerdo (Corte Físico + Caixa de Controle 3D)
# ---------------------------------------------------------------------------
def _draw_left_panel(ax):
    xc_L = -4.32

    # Cabeçalho do Painel 1
    crisp_text(
        ax, xc_L, 4.52,
        r"1. Significado Físico na Coluna d'Água: Inclinação nas Faces e Balanço de Volume",
        color=PALETTE["navy_deep"], stroke_w=0.20,
        fontsize=10.5, fontweight="bold", ha="center", va="bottom", zorder=30,
    )
    crisp_text(
        ax, xc_L, 4.25,
        r"O gradiente $\nabla_h\eta$ impulsiona o escoamento nas faces; a divergência $\nabla_h\cdot\mathbf{q}$ governa a variação de $\eta$ no centro",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.7, ha="center", va="top", zorder=30,
    )

    # =======================================================================
    # 1A. CORTE LONGITUDINAL / DEGRAU DE CASULLI + RAMPA DO GRADIENTE
    # =======================================================================
    crisp_text(
        ax, -8.25, 3.80,
        r"a) Corte Físico: Degrau Batimétrico ($h = 0{,}5\,\mathrm{m} \rightarrow 5{,}0\,\mathrm{m}$), Rampa $\nabla_h\eta$ e Fluxo $q_x = H_u u$",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.95, fontweight="bold", ha="left", va="bottom", zorder=28,
    )

    # Três células adjacentes no corte longitudinal:
    #   Célula i-1 (Planície rasa): [-7.95, -5.55], centro -6.75
    #   Célula i   (Canal):         [-5.55, -3.15], centro -4.35
    #   Célula i+1 (Canal):         [-3.15, -0.75], centro -1.95
    x_left, x_step, x_face_u, x_right = -7.95, -5.55, -3.15, -0.75
    xc_s, xc_i, xc_ip1 = -6.75, -4.35, -1.95

    y_rock = 0.56
    y_bed_shelf = 2.20   # Planície rasa (h = 0,5 m abaixo de z=0)
    y_bed_chan = 1.04    # Canal profundo (h = 5,0 m abaixo de z=0)
    y_datum = 2.60       # Nível médio de referência não perturbado (eta = 0)

    xs_wave = np.linspace(x_left - 0.12, x_right + 0.12, 320)

    def surf_y(x):
        ramp = -0.30 * np.tanh((x - x_face_u) / 1.15)
        ripple = 0.05 * np.sin(1.45 * (x - x_left))
        return y_datum + 0.05 + ramp + ripple

    ys_wave = surf_y(xs_wave)
    y_eta_s = float(surf_y(xc_s))
    y_eta_i = float(surf_y(xc_i))
    y_eta_ip1 = float(surf_y(xc_ip1))
    y_face_step = float(surf_y(x_step))

    # Preenchimento da coluna d'água: Planície rasa vs. Canal profundo
    mask_shelf = xs_wave <= x_step
    xs_sh = np.append(xs_wave[mask_shelf], x_step)
    ys_sh = np.append(ys_wave[mask_shelf], y_face_step)
    ax.add_patch(Polygon(
        [(xs_sh[0], y_bed_shelf)] + list(zip(xs_sh, ys_sh)) + [(x_step, y_bed_shelf)],
        closed=True, facecolor=PALETTE["water_body"], edgecolor="none", alpha=0.72, zorder=4
    ))

    mask_chan = xs_wave >= x_step
    xs_ch = np.insert(xs_wave[mask_chan], 0, x_step)
    ys_ch = np.insert(ys_wave[mask_chan], 0, y_face_step)
    ax.add_patch(Polygon(
        [(x_step, y_bed_chan)] + list(zip(xs_ch, ys_ch)) + [(xs_ch[-1], y_bed_chan)],
        closed=True, facecolor=PALETTE["water_deep"], edgecolor="none", alpha=0.78, zorder=4
    ))

    # Destaque suave na célula (i, j) do canal [-5.55, -3.15]
    xs_ci = np.linspace(x_step, x_face_u, 80)
    ax.add_patch(Polygon(
        [(x_step, y_bed_chan)] + list(zip(xs_ci, surf_y(xs_ci))) + [(x_face_u, y_bed_chan)],
        closed=True, facecolor="#DCECF7", edgecolor="none", alpha=0.42, zorder=4.5
    ))

    # Bloco geológico com degrau entre planície rasa e canal profundo
    poly_bed = [
        (x_left - 0.12, y_rock),
        (x_right + 0.12, y_rock),
        (x_right + 0.12, y_bed_chan),
        (x_step, y_bed_chan),
        (x_step, y_bed_shelf),
        (x_left - 0.12, y_bed_shelf),
    ]
    ax.add_patch(Polygon(
        poly_bed, closed=True, facecolor=PALETTE["bed_front"], edgecolor="none", zorder=5
    ))
    ax.plot(
        [x_left - 0.12, x_step, x_step, x_right + 0.12],
        [y_bed_shelf, y_bed_shelf, y_bed_chan, y_bed_chan],
        color=PALETTE["bed_edge"], lw=1.45, zorder=8,
    )

    # Hachuras geológicas curtas (deixando faixa inferior limpa para o rótulo do canal)
    for xh in np.linspace(x_left + 0.06, x_step - 0.12, 11):
        ax.plot([xh, xh - 0.11], [y_bed_shelf, y_bed_shelf - 0.18],
                color=PALETTE["bed_hatch"], lw=0.48, alpha=0.70, zorder=6)
    for yh in np.linspace(y_bed_chan + 0.18, y_bed_shelf - 0.12, 6):
        ax.plot([x_step, x_step - 0.13], [yh, yh - 0.14],
                color=PALETTE["bed_hatch"], lw=0.48, alpha=0.70, zorder=6)
    for xh in np.linspace(x_step + 0.18, x_right - 0.04, 19):
        ax.plot([xh, xh - 0.10], [y_bed_chan, y_bed_chan - 0.15],
                color=PALETTE["bed_hatch"], lw=0.48, alpha=0.70, zorder=6)

    # Curva da superfície livre ondulante eta(x)
    ax.plot(xs_wave, ys_wave, color=PALETTE["water_edge"], lw=2.1, zorder=12)

    # Linha de referência não perturbada (eta = 0) com rótulo limpo à esquerda/centro
    ax.plot(
        [x_left - 0.16, x_right + 0.16], [y_datum, y_datum],
        color=PALETTE["rule_dark"], lw=0.85, ls=(0, (5, 3)), alpha=0.78, zorder=9,
    )
    crisp_text(
        ax, -7.86, y_datum - 0.07, r"Nível médio ($\eta = 0$)",
        color=PALETTE["rule_dark"], stroke_w=0.12, bg_pill=PALETTE["water_body"], pad=0.04,
        fontsize=7.55, fontstyle="italic", ha="left", va="top", zorder=18,
    )

    # Faces verticais das células (tracejadas)
    for xf_v, y_bot_v in [
        (x_left, y_bed_shelf),
        (x_step, y_bed_chan),
        (x_face_u, y_bed_chan),
        (x_right, y_bed_chan),
    ]:
        lw_f = 1.25 if xf_v in (x_step, x_face_u) else 0.85
        col_f = PALETTE["water_edge"] if xf_v == x_face_u else PALETTE["cell_border"]
        ax.plot([xf_v, xf_v], [y_bot_v, surf_y(xf_v) + 0.12],
                color=col_f, lw=lw_f, ls="--", alpha=0.82, zorder=10)

    # Pontos escalares nos centros na superfície livre (eta)
    for xc_k, yk in [(xc_s, y_eta_s), (xc_i, y_eta_i), (xc_ip1, y_eta_ip1)]:
        ax.plot(xc_k, yk, marker="o", markersize=6.4,
                markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
                markeredgewidth=1.0, zorder=16)

    crisp_text(
        ax, xc_s, y_eta_s + 0.10, r"$\eta_{i-1,j}$",
        color=PALETTE["z_node"], stroke_w=0.15, bg_pill=PALETTE["bg_canvas"], pad=0.05,
        fontsize=8.2, fontweight="bold", ha="center", va="bottom", zorder=20,
    )
    crisp_text(
        ax, xc_i, y_eta_i + 0.10, r"$\eta_{i,j}$ (mais alto)",
        color=PALETTE["z_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.06,
        fontsize=8.25, fontweight="bold", ha="center", va="bottom", zorder=20,
    )
    # Rótulo de eta_{i+1,j} acima da superfície livre em espaço totalmente aberto
    crisp_text(
        ax, xc_ip1 + 0.12, y_eta_ip1 + 0.11, r"$\eta_{i+1,j}$ (mais baixo)",
        color=PALETTE["z_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.05,
        fontsize=8.1, fontweight="bold", ha="center", va="bottom", zorder=22,
    )

    # Cota geométrica do desnível Delta eta posicionada em x_d = -2.62 (entre a face e i+1)
    x_d_eta = -2.58
    ax.plot([xc_i + 0.08, x_d_eta + 0.08], [y_eta_i, y_eta_i],
            color=PALETTE["z_node"], lw=0.85, ls=":", zorder=14)
    ax.plot([x_d_eta - 0.08, xc_ip1 - 0.06], [y_eta_ip1, y_eta_ip1],
            color=PALETTE["z_node"], lw=0.85, ls=":", zorder=14)
    draw_arrow(
        ax, (x_d_eta, y_eta_i), (x_d_eta, y_eta_ip1 + 0.03),
        color=PALETTE["z_node"], lw=1.30, mutation_scale=9.5, arrowstyle="-|>", zorder=18
    )
    crisp_text(
        ax, x_d_eta + 0.10, y_eta_i + 0.08,
        r"Desnível $\Delta\eta = \eta_{i+1,j} - \eta_{i,j} < 0$",
        color=PALETTE["z_node"], stroke_w=0.15, bg_pill=PALETTE["bg_canvas"], pad=0.06,
        fontsize=7.95, fontweight="bold", ha="center", va="bottom", zorder=22,
    )

    # Marcador de velocidade u na face x_{i+1/2} + Seta de empuxo hidrostático -g G_x eta
    y_thrust = 1.90
    ax.plot(x_face_u, y_thrust, marker="s", markersize=6.2,
            markerfacecolor=PALETTE["u_node"], markeredgecolor="white",
            markeredgewidth=1.0, zorder=22)
    draw_arrow(
        ax, (x_face_u - 0.70, y_thrust), (x_face_u + 0.74, y_thrust),
        color=PALETTE["u_node"], lw=2.3, mutation_scale=12.5, zorder=21
    )
    crisp_text(
        ax, x_face_u, y_thrust + 0.13,
        r"Empuxo $-g(G_x\eta)_{i+1/2,j}$ na face $u$",
        color=PALETTE["u_node"], stroke_w=0.17, bg_pill="#F9EFEA", pad=0.07,
        fontsize=8.0, fontweight="bold", ha="center", va="bottom", zorder=24,
    )

    # Contraste de Fluxo Volumétrico: Face rasa (x_step) vs. Face profunda (x_face_u)
    y_mid_sh = 0.5 * (y_bed_shelf + y_face_step) + 0.02
    ax.plot(x_step, y_mid_sh, marker="s", markersize=5.4,
            markerfacecolor=PALETTE["u_node"], markeredgecolor="white",
            markeredgewidth=0.9, zorder=22)
    draw_arrow(
        ax, (x_step - 0.36, y_mid_sh), (x_step + 0.38, y_mid_sh),
        color=PALETTE["u_node"], lw=1.40, mutation_scale=9.0, zorder=21
    )
    # Linha-guia limpa apontando diretamente para o nó u da face rasa x_step
    ax.plot([x_step, x_step - 0.34], [y_mid_sh + 0.08, 3.36],
            color=PALETTE["u_node"], lw=0.75, ls="-", zorder=18)
    crisp_text(
        ax, x_step - 0.36, 3.38,
        r"Face rasa: $q_x = H_u u$ pequeno",
        color=PALETTE["u_node"], stroke_w=0.14, bg_pill="#F9EFEA", pad=0.06,
        fontsize=7.75, fontweight="bold", ha="center", va="bottom", zorder=22,
    )

    # Vetores distribuídos na coluna profunda mostrando transporte volumétrico H_u * u
    for y_sub in (1.28, 1.58):
        draw_arrow(
            ax, (x_face_u - 0.45, y_sub), (x_face_u + 0.48, y_sub),
            color=PALETTE["water_edge"], lw=1.15, mutation_scale=8.5, alpha=0.80, zorder=15
        )
    # Chave vertical H_u na coluna profunda
    x_brk_H = x_step + 0.28
    draw_arrow(
        ax, (x_brk_H, y_bed_chan + 0.03), (x_brk_H, surf_y(x_brk_H) - 0.03),
        color=PALETTE["navy_deep"], lw=1.05, mutation_scale=8.5, arrowstyle="<|-|>", zorder=17
    )
    crisp_text(
        ax, x_brk_H + 0.09, 1.48,
        r"$H_u = h_u + \eta_u$",
        color=PALETTE["navy_deep"], stroke_w=0.15, bg_pill="#CBE3F0", pad=0.05,
        fontsize=7.95, fontweight="bold", ha="left", va="center", zorder=19,
    )

    # Rótulos da batimetria de Casulli perfeitamente contidos no bloco do solo sem hachuras
    crisp_text(
        ax, xc_s, 1.42,
        "Planície rasa\n" + r"$h = 0{,}5\,\mathrm{m}$",
        color="#33281E", stroke_w=0.14,
        fontsize=8.1, fontweight="bold", ha="center", va="center", linespacing=1.18, zorder=15,
    )
    crisp_text(
        ax, 0.5 * (x_step + x_right), 0.71,
        r"Canal profundo ($h = 5{,}0\,\mathrm{m}$): $H_u$ multiplica $u$ para medir volume ($\sim\!10\times$ maior que na planície)",
        color="#2B2118", stroke_w=0.13,
        fontsize=7.45, fontstyle="italic", ha="center", va="center", zorder=15,
    )

    # Linha divisória horizontal interna entre 1a e 1b
    ax.plot([-8.25, -0.38], [0.38, 0.38], color=PALETTE["rule_light"], lw=0.85, zorder=5)

    # =======================================================================
    # 1B. CAIXA DE CONTROLE 3D: DIVERGÊNCIA DOS FLUXOS (Dq) E NÍVEL ETA
    # =======================================================================
    crisp_text(
        ax, -8.25, 0.10,
        r"b) Caixa de Controle 3D ($\Delta x \times \Delta y$, altura $H = h + \eta$): Saldo de Fluxos Governa $\partial\eta/\partial t$",
        color=PALETTE["navy_deep"], stroke_w=0.17,
        fontsize=8.95, fontweight="bold", ha="left", va="bottom", zorder=28,
    )

    orig_3d = (-6.58, -2.55)
    dx3, dy3 = 2.22, 1.70
    z_bed3, z_rock3 = -1.16, -1.54
    z_t0, z_t1 = 0.20, 0.65

    # Base geológica 3D
    ax.add_patch(Polygon(
        [proj3d(0, 0, z_rock3, orig_3d), proj3d(dx3, 0, z_rock3, orig_3d),
         proj3d(dx3, 0, z_bed3, orig_3d), proj3d(0, 0, z_bed3, orig_3d)],
        facecolor=PALETTE["bed_front"], edgecolor=PALETTE["bed_edge"], lw=0.9, zorder=5
    ))
    ax.add_patch(Polygon(
        [proj3d(dx3, 0, z_rock3, orig_3d), proj3d(dx3, dy3, z_rock3, orig_3d),
         proj3d(dx3, dy3, z_bed3, orig_3d), proj3d(dx3, 0, z_bed3, orig_3d)],
        facecolor=PALETTE["bed_right"], edgecolor=PALETTE["bed_edge"], lw=0.9, zorder=5
    ))
    ax.add_patch(Polygon(
        [proj3d(0, 0, z_bed3, orig_3d), proj3d(dx3, 0, z_bed3, orig_3d),
         proj3d(dx3, dy3, z_bed3, orig_3d), proj3d(0, dy3, z_bed3, orig_3d)],
        facecolor=PALETTE["bed_top"], edgecolor=PALETTE["bed_edge"], lw=0.7, alpha=0.9, zorder=4
    ))
    for xh in np.linspace(0.20, dx3 - 0.20, 9):
        ax.plot(*proj3d([xh, xh - 0.11], [0, 0], [z_bed3, z_bed3 - 0.24], orig_3d),
                color=PALETTE["bed_hatch"], lw=0.45, alpha=0.7, zorder=5.5)
    for yh in np.linspace(0.20, dy3 - 0.20, 7):
        ax.plot(*proj3d([dx3, dx3], [yh, yh - 0.11], [z_bed3, z_bed3 - 0.24], orig_3d),
                color="#736354", lw=0.45, alpha=0.7, zorder=5.5)

    # Corpo principal da coluna de água até z_t0
    ax.add_patch(Polygon(
        [proj3d(0, 0, z_bed3, orig_3d), proj3d(dx3, 0, z_bed3, orig_3d),
         proj3d(dx3, 0, z_t0, orig_3d), proj3d(0, 0, z_t0, orig_3d)],
        facecolor=PALETTE["water_front"], edgecolor="none", alpha=0.48, zorder=10
    ))
    ax.add_patch(Polygon(
        [proj3d(dx3, 0, z_bed3, orig_3d), proj3d(dx3, dy3, z_bed3, orig_3d),
         proj3d(dx3, dy3, z_t0, orig_3d), proj3d(dx3, 0, z_t0, orig_3d)],
        facecolor=PALETTE["water_right"], edgecolor="none", alpha=0.54, zorder=10
    ))

    # Camada superior de variação volumétrica (entre z_t0 e z_t1)
    ax.add_patch(Polygon(
        [proj3d(0, 0, z_t0, orig_3d), proj3d(dx3, 0, z_t0, orig_3d),
         proj3d(dx3, 0, z_t1, orig_3d), proj3d(0, 0, z_t1, orig_3d)],
        facecolor="#88BBD8", edgecolor="none", alpha=0.55, zorder=11
    ))
    ax.add_patch(Polygon(
        [proj3d(dx3, 0, z_t0, orig_3d), proj3d(dx3, dy3, z_t0, orig_3d),
         proj3d(dx3, dy3, z_t1, orig_3d), proj3d(dx3, 0, z_t1, orig_3d)],
        facecolor="#72A8C8", edgecolor="none", alpha=0.55, zorder=11
    ))

    # Topo da superfície livre em z_t1 + contorno tracejado em z_t0
    ax.add_patch(Polygon(
        [proj3d(0, 0, z_t1, orig_3d), proj3d(dx3, 0, z_t1, orig_3d),
         proj3d(dx3, dy3, z_t1, orig_3d), proj3d(0, dy3, z_t1, orig_3d)],
        facecolor=PALETTE["water_top"], edgecolor=PALETTE["water_edge"], lw=1.35, alpha=0.85, zorder=14
    ))
    pts_t0 = [proj3d(0, 0, z_t0, orig_3d), proj3d(dx3, 0, z_t0, orig_3d),
              proj3d(dx3, dy3, z_t0, orig_3d), proj3d(0, dy3, z_t0, orig_3d),
              proj3d(0, 0, z_t0, orig_3d)]
    ax.plot([p[0] for p in pts_t0], [p[1] for p in pts_t0],
            color=PALETTE["water_edge"], lw=0.95, ls="--", alpha=0.85, zorder=15)

    # Arestas verticais frontais e linha eta = 0
    for (xe, ye), lwe in [((0, 0), 1.2), ((dx3, 0), 1.3), ((dx3, dy3), 1.15)]:
        ax.plot(*proj3d([xe, xe], [ye, ye], [z_rock3, z_t1], orig_3d),
                color=PALETTE["water_edge"], lw=lwe, zorder=16)
    ax.plot(*proj3d([0, dx3], [0, 0], [0, 0], orig_3d),
            color=PALETTE["rule_dark"], lw=0.90, ls=(0, (4, 3)), zorder=16)
    ax.plot(*proj3d([dx3, dx3], [0, dy3], [0, 0], orig_3d),
            color=PALETTE["rule_dark"], lw=0.90, ls=(0, (4, 3)), zorder=16)
    p_eta0 = proj3d(dx3, 0, 0, orig_3d)
    crisp_text(ax, p_eta0[0] - 0.12, p_eta0[1] + 0.06, r"$\eta = 0$",
               color=PALETTE["rule_dark"], stroke_w=0.13, bg_pill="#C8E1F0", pad=0.03,
               fontsize=7.6, ha="right", va="bottom", zorder=22)

    # Nó central eta_{i,j} e setas verticais (sobe / desce)
    p_top_c = proj3d(0.5 * dx3, 0.5 * dy3, z_t1, orig_3d)
    ax.plot(p_top_c[0], p_top_c[1], marker="o", markersize=6.8,
            markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
            markeredgewidth=1.0, zorder=22)
    draw_3d_arrow(ax, (0.34 * dx3, 0.45 * dy3, z_t0 - 0.02), (0.34 * dx3, 0.45 * dy3, z_t1 + 0.30),
                  orig_3d, color=PALETTE["z_node"], lw=1.9, mutation_scale=10.5, zorder=21)
    draw_3d_arrow(ax, (0.68 * dx3, 0.52 * dy3, z_t1 + 0.22), (0.68 * dx3, 0.52 * dy3, z_t0 - 0.10),
                  orig_3d, color=PALETTE["u_node"], lw=1.7, mutation_scale=10.0, ls="-", zorder=21)
    crisp_text(
        ax, p_top_c[0] - 0.10, p_top_c[1] + 0.42,
        r"$\eta_{i,j}$ sobe ($\uparrow$) ou desce ($\downarrow$)",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.06,
        fontsize=8.2, fontweight="bold", ha="center", va="bottom", zorder=24,
    )

    # Fluxos q_x (faces verticais) e q_y (faces horizontais) entrando/saindo da célula
    zf = -0.52
    draw_3d_arrow(ax, (-0.92, 0.46 * dy3, zf), (0.04, 0.46 * dy3, zf),
                  orig_3d, color=PALETTE["u_node"], lw=2.3, mutation_scale=12.5, zorder=20)
    draw_3d_arrow(ax, (dx3 - 0.04, 0.46 * dy3, zf), (dx3 + 0.68, 0.46 * dy3, zf),
                  orig_3d, color=PALETTE["u_node"], lw=1.55, mutation_scale=10.5, zorder=20)
    draw_3d_arrow(ax, (0.42 * dx3, -0.86, zf - 0.08), (0.42 * dx3, 0.12, zf - 0.08),
                  orig_3d, color=PALETTE["v_node"], lw=2.1, mutation_scale=11.5, zorder=20)
    draw_3d_arrow(ax, (0.42 * dx3, dy3 - 0.04, zf + 0.04), (0.42 * dx3, dy3 + 0.70, zf + 0.04),
                  orig_3d, color=PALETTE["v_node"], lw=1.45, mutation_scale=9.5, zorder=7)

    p_qxin = proj3d(-0.56, 0.46 * dy3, zf + 0.18, orig_3d)
    crisp_text(ax, p_qxin[0] - 0.12, p_qxin[1] + 0.04, r"$q_{x,\mathrm{ent}} = H_u u$",
               color=PALETTE["u_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.0, fontweight="bold", ha="center", va="bottom", zorder=25)

    p_qxout = proj3d(dx3 + 0.70, 0.46 * dy3, zf, orig_3d)
    crisp_text(ax, p_qxout[0] + 0.03, p_qxout[1], r"$q_{x,\mathrm{sai}}$",
               color=PALETTE["u_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.2, fontweight="bold", ha="left", va="center", zorder=25)

    p_qyin = proj3d(0.42 * dx3 + 0.08, -0.46, zf - 0.22, orig_3d)
    crisp_text(ax, p_qyin[0] + 0.05, p_qyin[1] - 0.04, r"$q_{y,\mathrm{ent}} = H_v v$",
               color=PALETTE["v_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.0, fontweight="bold", ha="left", va="top", zorder=25)

    p_qyout = proj3d(0.42 * dx3 + 0.24, dy3 + 0.54, zf + 0.05, orig_3d)
    crisp_text(ax, p_qyout[0], p_qyout[1] + 0.04, r"$q_{y,\mathrm{sai}}$",
               color=PALETTE["v_node"], stroke_w=0.15, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.0, fontweight="bold", ha="left", va="bottom", zorder=25)

    # Cotas H = h + eta à esquerda, dx e dy na base da coluna 3D
    p_htop = proj3d(0, 0, z_t1, orig_3d)
    p_hbot = proj3d(0, 0, z_bed3, orig_3d)
    x_hbrk = p_htop[0] - 0.96
    ax.plot([p_htop[0], x_hbrk - 0.06], [p_htop[1], p_htop[1]], color=PALETTE["ink_muted"], lw=0.55, zorder=15)
    ax.plot([p_hbot[0], x_hbrk - 0.06], [p_hbot[1], p_hbot[1]], color=PALETTE["ink_muted"], lw=0.55, zorder=15)
    draw_arrow(ax, (x_hbrk, p_hbot[1]), (x_hbrk, p_htop[1]),
               color=PALETTE["ink_primary"], lw=0.95, mutation_scale=8.0, arrowstyle="<|-|>", zorder=18)
    crisp_text(ax, x_hbrk - 0.08, 0.5 * (p_htop[1] + p_hbot[1]),
               r"$H = h + \eta$", rotation=90,
               color=PALETTE["ink_primary"], stroke_w=0.16,
               fontsize=8.3, fontweight="bold", ha="right", va="center", zorder=22)

    p_dx0 = proj3d(0, 0, z_rock3 - 0.14, orig_3d)
    p_dx1 = proj3d(dx3, 0, z_rock3 - 0.14, orig_3d)
    draw_arrow(ax, p_dx0, p_dx1, color=PALETTE["ink_muted"], lw=0.9, mutation_scale=8.0, arrowstyle="<|-|>")
    crisp_text(ax, 0.5 * (p_dx0[0] + p_dx1[0]) - 0.06, 0.5 * (p_dx0[1] + p_dx1[1]) - 0.08,
               r"$\Delta x$", color=PALETTE["ink_primary"], stroke_w=0.15, fontsize=8.4, ha="center", va="top")

    p_dy0 = proj3d(dx3 + 0.12, 0, z_rock3 - 0.08, orig_3d)
    p_dy1 = proj3d(dx3 + 0.12, dy3, z_rock3 - 0.08, orig_3d)
    draw_arrow(ax, p_dy0, p_dy1, color=PALETTE["ink_muted"], lw=0.9, mutation_scale=8.0, arrowstyle="<|-|>")
    crisp_text(ax, 0.5 * (p_dy0[0] + p_dy1[0]) + 0.12, 0.5 * (p_dy0[1] + p_dy1[1]) - 0.06,
               r"$\Delta y$", color=PALETTE["ink_primary"], stroke_w=0.15, fontsize=8.4, ha="left", va="top")

    # Síntese editorial aberta (estilo Tufte booktabs, sem bordas laterais pesadas)
    x_syn = -2.84
    ax.plot([x_syn - 0.10, -0.38], [-0.32, -0.32], color=PALETTE["rule_dark"], lw=1.15, zorder=6)
    ax.plot([x_syn - 0.10, -0.38], [-4.66, -4.66], color=PALETTE["rule_dark"], lw=1.15, zorder=6)

    crisp_text(
        ax, x_syn + 1.14, -0.56,
        "Balanço Volumétrico Local",
        color=PALETTE["navy_deep"], stroke_w=0.17,
        fontsize=8.6, fontweight="bold", ha="center", va="center", zorder=15,
    )
    crisp_text(
        ax, x_syn + 1.14, -1.06,
        r"$\dfrac{\partial \eta_{i,j}}{\partial t} = -(D\mathbf{q})_{i,j}$",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_pill=PALETTE["panel_tint"], pad=0.12,
        fontsize=9.3, ha="center", va="center", zorder=15,
    )

    ax.plot([x_syn, -0.48], [-1.56, -1.56], color=PALETTE["rule_light"], lw=0.75, zorder=6)

    crisp_text(
        ax, x_syn + 0.02, -1.82,
        r"$\bullet\;$ Entra $>$ Sai ($D\mathbf{q} < 0$):",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.35, fontweight="bold", ha="left", va="center", zorder=15,
    )
    crisp_text(
        ax, x_syn + 0.16, -2.10,
        "Acúmulo líquido de água na\n" + r"célula $\Rightarrow$ nível $\eta_{i,j}$ sobe ($\uparrow$).",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.9, ha="left", va="top", linespacing=1.24, zorder=15,
    )

    crisp_text(
        ax, x_syn + 0.02, -2.96,
        r"$\bullet\;$ Sai $>$ Entra ($D\mathbf{q} > 0$):",
        color=PALETTE["u_node"], stroke_w=0.17,
        fontsize=8.35, fontweight="bold", ha="left", va="center", zorder=15,
    )
    crisp_text(
        ax, x_syn + 0.16, -3.24,
        "Déficit de água no volume\n" + r"$\Delta x\Delta y \Rightarrow$ nível $\eta_{i,j}$ desce ($\downarrow$).",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.9, ha="left", va="top", linespacing=1.24, zorder=15,
    )

    ax.plot([x_syn, -0.48], [-3.96, -3.96], color=PALETTE["rule_light"], lw=0.75, zorder=6)
    crisp_text(
        ax, x_syn + 1.14, -4.31,
        "Fluxos por unidade de largura:\n" + r"$q_x = H_u u$, $\;q_y = H_v v\;\;(\mathrm{m^2/s})$",
        color=PALETTE["ink_muted"], stroke_w=0.12,
        fontsize=7.75, fontstyle="italic", ha="center", va="center", linespacing=1.22, zorder=15,
    )


# ---------------------------------------------------------------------------
# 5. Construção do Painel Direito (Estêncil Escalonado + Cancelamento Telescópico)
# ---------------------------------------------------------------------------
def _draw_right_panel(ax):
    xc_R = 4.22

    # Cabeçalho do Painel 2 (usando \mathbf{R} clássico de TeX / Seção 2.1)
    crisp_text(
        ax, xc_R, 4.52,
        r"2. Célula Unitária na Malha Escalonada e Conservação por Cancelamento Telescópico",
        color=PALETTE["z_node"], stroke_w=0.20,
        fontsize=10.5, fontweight="bold", ha="center", va="bottom", zorder=30,
    )
    crisp_text(
        ax, xc_R, 4.25,
        r"Indexação NumPy $[j, i]$: $\eta \in \mathbf{R}^{N_y \times N_x}$ (centros), $u/q_x \in \mathbf{R}^{N_y \times (N_x+1)}$ (faces vert.) e $v/q_y \in \mathbf{R}^{(N_y+1) \times N_x}$ (faces horiz.)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.6, ha="center", va="top", zorder=30,
    )

    # =======================================================================
    # 2A. ESTÊNCIL 5-CÉLULAS (CRUZ) + ACOPLAMENTO G_x, G_y E Dq
    # =======================================================================
    crisp_text(
        ax, 0.18, 3.80,
        r"a) Célula $(i, j)$ e Vizinhos Imediatos: Diferenças de $(G_x\eta)$, $(G_y\eta)$ nas Faces e $(D\mathbf{q})$ no Centro",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.95, fontweight="bold", ha="left", va="bottom", zorder=28,
    )

    cx, cy = 2.62, 1.32
    W_c, H_c = 2.04, 1.78
    W_nb, H_nb = 1.16, 0.96

    xL, xR = cx - 0.5 * W_c, cx + 0.5 * W_c
    yB, yT = cy - 0.5 * H_c, cy + 0.5 * H_c

    # 4 células vizinhas (esquerda i-1, direita i+1, acima j+1, abaixo j-1)
    for rx, ry, rw, rh in [
        (xL - W_nb, yB, W_nb, H_c),
        (xR, yB, W_nb, H_c),
        (xL, yT, W_c, H_nb),
        (xL, yB - H_nb, W_c, H_nb),
    ]:
        ax.add_patch(Rectangle(
            (rx, ry), rw, rh,
            facecolor=PALETTE["cell_bg"], edgecolor=PALETTE["cell_border"],
            lw=0.90, ls="--", alpha=0.88, zorder=4
        ))

    # Célula central (i, j)
    ax.add_patch(Rectangle(
        (xL, yB), W_c, H_c,
        facecolor=PALETTE["cell_focus"], edgecolor=PALETTE["water_edge"],
        lw=1.80, zorder=6
    ))

    # Eixos guias pontilhados cruzando os centros
    ax.plot([xL - 0.72 * W_nb, xR + 0.72 * W_nb], [cy, cy],
            color=PALETTE["ink_muted"], lw=0.65, ls=":", zorder=7)
    ax.plot([cx, cx], [yB - 0.72 * H_nb, yT + 0.72 * H_nb],
            color=PALETTE["ink_muted"], lw=0.65, ls=":", zorder=7)

    # Setas internas pontilhadas mostrando que as 4 faces alimentam (Dq)_{i,j} no centro
    for p_from, p_to in [
        ((xL + 0.24, cy), (cx - 0.36, cy)),
        ((xR - 0.24, cy), (cx + 0.36, cy)),
        ((cx, yB + 0.22), (cx, cy - 0.32)),
        ((cx, yT - 0.22), (cx, cy + 0.32)),
    ]:
        draw_arrow(
            ax, p_from, p_to, color=PALETTE["z_node"],
            lw=0.95, mutation_scale=7.5, ls=":", alpha=0.75, zorder=12
        )

    # Marcadores nos centros das células: círculos azul-cerúleo ('o')
    xc_im1 = xL - 0.55 * W_nb
    xc_ip1 = xR + 0.55 * W_nb
    yc_jp1 = yT + 0.52 * H_nb
    yc_jm1 = yB - 0.52 * H_nb

    ax.plot(cx, cy, marker="o", markersize=8.0,
            markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
            markeredgewidth=1.2, zorder=20)
    crisp_text(
        ax, cx, cy + 0.13, r"$\eta_{i,j}$",
        color=PALETTE["z_node"], stroke_w=0.19, bg_pill=PALETTE["cell_focus"], pad=0.04,
        fontsize=9.8, fontweight="bold", ha="center", va="bottom", zorder=22,
    )
    crisp_text(
        ax, cx, cy - 0.13, r"$(D\mathbf{q})_{i,j}$",
        color=PALETTE["navy_deep"], stroke_w=0.16, bg_pill=PALETTE["cell_focus"], pad=0.04,
        fontsize=8.4, fontweight="bold", ha="center", va="top", zorder=22,
    )

    for nx_p, ny_p, lbl_p, dx_off, dy_off, ha_p, va_p in [
        (xc_im1, cy, r"$\eta_{i-1,j}$", 0.0, 0.13, "center", "bottom"),
        (xc_ip1, cy, r"$\eta_{i+1,j}$", 0.0, 0.13, "center", "bottom"),
        (cx, yc_jp1, r"$\eta_{i,j+1}$", 0.14, 0.0, "left", "center"),
        (cx, yc_jm1, r"$\eta_{i,j-1}$", 0.14, 0.0, "left", "center"),
    ]:
        ax.plot(nx_p, ny_p, marker="o", markersize=6.2,
                markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
                markeredgewidth=1.0, zorder=18)
        crisp_text(
            ax, nx_p + dx_off, ny_p + dy_off, lbl_p,
            color=PALETTE["z_node"], stroke_w=0.15, bg_pill=PALETTE["cell_bg"], pad=0.04,
            fontsize=8.5, fontweight="bold", ha=ha_p, va=va_p, zorder=20,
        )

    # Faces verticais: quadrados terracota ('s') + setas de fluxo q_x
    for xf_u, q_lbl in [
        (xL, r"$q_{x, i-1/2, j}$"),
        (xR, r"$q_{x, i+1/2, j}$"),
    ]:
        draw_arrow(
            ax, (xf_u - 0.28, cy), (xf_u + 0.32, cy),
            color=PALETTE["u_node"], lw=2.1, mutation_scale=11.0, zorder=23
        )
        ax.plot(xf_u, cy, marker="s", markersize=6.0,
                markerfacecolor=PALETTE["u_node"], markeredgecolor="white",
                markeredgewidth=0.95, zorder=24)
        crisp_text(
            ax, xf_u, cy - 0.22, q_lbl,
            color=PALETTE["u_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.05,
            fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=25,
        )

    # Faces horizontais: triângulos verde-petróleo ('^') + setas de fluxo q_y
    for yf_v, q_lbl in [
        (yT, r"$q_{y, i, j+1/2}$"),
        (yB, r"$q_{y, i, j-1/2}$"),
    ]:
        draw_arrow(
            ax, (cx, yf_v - 0.25), (cx, yf_v + 0.29),
            color=PALETTE["v_node"], lw=2.1, mutation_scale=11.0, zorder=23
        )
        ax.plot(cx, yf_v, marker="^", markersize=6.8,
                markerfacecolor=PALETTE["v_node"], markeredgecolor="white",
                markeredgewidth=0.95, zorder=24)
        crisp_text(
            ax, cx + 0.18, yf_v + (0.10 if yf_v == yT else -0.10), q_lbl,
            color=PALETTE["v_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.05,
            fontsize=8.3, fontweight="bold", ha="left",
            va="bottom" if yf_v == yT else "top", zorder=25,
        )

    # Setas curtas nos quadrantes livres mostrando a composição de G_x eta e G_y eta:
    # 1) Quadrante superior-direito: (G_x eta)_{i+1/2, j}
    draw_arrow(
        ax, (cx + 0.18, cy + 0.34), (xR - 0.04, cy + 0.56),
        color=PALETTE["u_node"], lw=1.15, mutation_scale=8.5,
        connectionstyle="arc3,rad=-0.18", zorder=22
    )
    draw_arrow(
        ax, (xc_ip1 - 0.10, cy + 0.32), (xR + 0.04, cy + 0.56),
        color=PALETTE["u_node"], lw=1.15, mutation_scale=8.5,
        connectionstyle="arc3,rad=0.18", zorder=22
    )
    crisp_text(
        ax, xR + 0.60, yT + 0.50,
        r"$(G_x\eta)_{i+1/2,j}$" + "\n" + r"$\leftarrow \eta_{i+1,j} - \eta_{i,j}$",
        color=PALETTE["u_node"], stroke_w=0.15, bg_pill="#F9EFEA", pad=0.09,
        border_col=PALETTE["u_node"], border_lw=0.65,
        fontsize=7.9, fontweight="bold", ha="center", va="center", linespacing=1.22, zorder=26,
    )
    ax.plot([xR, xR + 0.28], [cy + 0.58, yT + 0.24], color=PALETTE["u_node"], lw=0.80, zorder=21)

    # 2) Quadrante superior-esquerdo: (G_y eta)_{i, j+1/2}
    draw_arrow(
        ax, (cx - 0.28, cy + 0.22), (cx - 0.56, yT - 0.04),
        color=PALETTE["v_node"], lw=1.15, mutation_scale=8.5,
        connectionstyle="arc3,rad=0.18", zorder=22
    )
    draw_arrow(
        ax, (cx - 0.20, yc_jp1 - 0.06), (cx - 0.56, yT + 0.04),
        color=PALETTE["v_node"], lw=1.15, mutation_scale=8.5,
        connectionstyle="arc3,rad=-0.18", zorder=22
    )
    crisp_text(
        ax, xL - 0.58, yT + 0.50,
        r"$(G_y\eta)_{i,j+1/2}$" + "\n" + r"$\leftarrow \eta_{i,j+1} - \eta_{i,j}$",
        color=PALETTE["v_node"], stroke_w=0.15, bg_pill="#EBF4F3", pad=0.09,
        border_col=PALETTE["v_node"], border_lw=0.65,
        fontsize=7.9, fontweight="bold", ha="center", va="center", linespacing=1.22, zorder=26,
    )
    ax.plot([cx - 0.56, xL - 0.20], [yT, yT + 0.24], color=PALETTE["v_node"], lw=0.80, zorder=21)

    # Cotas dx e dy
    y_dx_dim = yB - H_nb - 0.20
    draw_arrow(ax, (xL, y_dx_dim), (xR, y_dx_dim),
               color=PALETTE["ink_muted"], lw=0.95, mutation_scale=8.5, arrowstyle="<|-|>", zorder=16)
    crisp_text(ax, cx, y_dx_dim - 0.06, r"$\Delta x$",
               color=PALETTE["ink_primary"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.6, ha="center", va="top", zorder=18)

    x_dy_dim = xL - W_nb - 0.18
    draw_arrow(ax, (x_dy_dim, yB), (x_dy_dim, yT),
               color=PALETTE["ink_muted"], lw=0.95, mutation_scale=8.5, arrowstyle="<|-|>", zorder=16)
    crisp_text(ax, x_dy_dim - 0.08, cy, r"$\Delta y$",
               color=PALETTE["ink_primary"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.04,
               fontsize=8.6, ha="right", va="center", zorder=18)

    # -----------------------------------------------------------------------
    # Coluna Lateral Direita (Equações Discretas e Formas dos Arrays NumPy)
    # -----------------------------------------------------------------------
    x_op = 5.08
    ax.plot([x_op - 0.12, x_op - 0.12], [-0.95, 3.45], color=PALETTE["rule_light"], lw=0.80, ls=":", zorder=5)

    ax.plot(x_op + 0.08, 3.30, marker="o", markersize=6.5,
            markerfacecolor=PALETTE["z_node"], markeredgecolor="white", markeredgewidth=0.9, zorder=20)
    crisp_text(
        ax, x_op + 0.24, 3.30,
        r"Centro Escalar — $(N_y, N_x)$:",
        color=PALETTE["z_node"], stroke_w=0.17,
        fontsize=8.45, fontweight="bold", ha="left", va="center", zorder=20,
    )
    crisp_text(
        ax, x_op + 0.24, 3.04,
        r"Elevação $\eta_{i,j}$, batimetria $h_{i,j}$ e $(D\mathbf{q})_{i,j}$.",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.9, ha="left", va="top", zorder=20,
    )

    ax.plot(x_op + 0.08, 2.52, marker="s", markersize=5.8,
            markerfacecolor=PALETTE["u_node"], markeredgecolor="white", markeredgewidth=0.9, zorder=20)
    crisp_text(
        ax, x_op + 0.24, 2.52,
        r"Gradiente Discreto ($G_h\eta$, faces internas):",
        color=PALETTE["u_node"], stroke_w=0.17,
        fontsize=8.45, fontweight="bold", ha="left", va="center", zorder=20,
    )
    crisp_text(
        ax, x_op + 0.24, 2.22,
        r"$(G_x\eta)_{i+1/2,j} = \dfrac{\eta_{i+1,j}-\eta_{i,j}}{\Delta x}\;\; (N_y, N_x\!-\!1)$",
        color=PALETTE["ink_primary"], stroke_w=0.14,
        fontsize=8.1, ha="left", va="top", zorder=20,
    )
    crisp_text(
        ax, x_op + 0.24, 1.62,
        r"$(G_y\eta)_{i,j+1/2} = \dfrac{\eta_{i,j+1}-\eta_{i,j}}{\Delta y}\;\; (N_y\!-\!1, N_x)$",
        color=PALETTE["ink_primary"], stroke_w=0.14,
        fontsize=8.1, ha="left", va="top", zorder=20,
    )

    ax.plot(x_op + 0.08, 0.96, marker="^", markersize=6.4,
            markerfacecolor=PALETTE["v_node"], markeredgecolor="white", markeredgewidth=0.9, zorder=20)
    crisp_text(
        ax, x_op + 0.24, 0.96,
        r"Fluxos nas Faces ($q_x, q_y$):",
        color=PALETTE["v_node"], stroke_w=0.17,
        fontsize=8.45, fontweight="bold", ha="left", va="center", zorder=20,
    )
    crisp_text(
        ax, x_op + 0.24, 0.70,
        r"$q_x$: $(N_y, N_x\!+\!1)$ $\cdot\;$ $q_y$: $(N_y\!+\!1, N_x)$" + "\n"
        + r"com $\eta_{i+1/2,j}^u = \frac{1}{2}(\eta_{i,j} + \eta_{i+1,j})$.",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.85, ha="left", va="top", linespacing=1.28, zorder=20,
    )

    crisp_text(
        ax, x_op + 0.06, -0.02,
        r"Divergência Discreta ($D\mathbf{q} \rightarrow$ centro):",
        color=PALETTE["navy_deep"], stroke_w=0.17,
        fontsize=8.45, fontweight="bold", ha="left", va="center", zorder=20,
    )
    crisp_text(
        ax, x_op + 0.06, -0.30,
        r"$(D\mathbf{q})_{i,j} = \dfrac{q_{x,i+1/2,j}-q_{x,i-1/2,j}}{\Delta x} + \dfrac{q_{y,i,j+1/2}-q_{y,i,j-1/2}}{\Delta y}$",
        color=PALETTE["ink_primary"], stroke_w=0.14,
        fontsize=7.85, ha="left", va="top", zorder=20,
    )

    # =======================================================================
    # 2B. QUADRO INFERIOR ESQUEMÁTICO: CANCELAMENTO TELESCÓPICO INTERNO
    # =======================================================================
    y_box_top = -1.32
    y_box_bot = -4.66
    ax.add_patch(Rectangle(
        (0.18, y_box_bot), 8.20, y_box_top - y_box_bot,
        facecolor=PALETTE["panel_card"], edgecolor="none", zorder=3
    ))
    ax.plot([0.18, 8.38], [y_box_top, y_box_top], color=PALETTE["rule_dark"], lw=1.20, zorder=8)
    ax.plot([0.18, 8.38], [y_box_bot, y_box_bot], color=PALETTE["rule_dark"], lw=1.20, zorder=8)

    crisp_text(
        ax, 0.30, y_box_top - 0.24,
        r"b) Conservação Discreta por Cancelamento Telescópico: Duas Células Adjacentes na Face Interna $x_{i+1/2}$",
        color=PALETTE["navy_deep"], stroke_w=0.17,
        fontsize=8.85, fontweight="bold", ha="left", va="center", zorder=20,
    )

    # Duas células adjacentes compartilhando a face vertical x_{i+1/2}
    xb0, xb_mid, xb1 = 0.64, 2.70, 4.76
    yb0, yb1 = -4.02, -1.96
    yc_tel = 0.5 * (yb0 + yb1)

    ax.add_patch(Rectangle(
        (xb0, yb0), xb_mid - xb0, yb1 - yb0,
        facecolor=PALETTE["cell_focus"], edgecolor=PALETTE["cell_border"], lw=1.15, zorder=5
    ))
    ax.add_patch(Rectangle(
        (xb_mid, yb0), xb1 - xb_mid, yb1 - yb0,
        facecolor=PALETTE["cell_bg"], edgecolor=PALETTE["cell_border"], lw=1.15, zorder=5
    ))

    # Face interna compartilhada destacada (terminando nitidamente em yb0, longe do texto inferior!)
    ax.plot([xb_mid, xb_mid], [yb0, yb1],
            color=PALETTE["u_node"], lw=2.45, zorder=14)
    ax.plot(xb_mid, yc_tel, marker="s", markersize=6.4,
            markerfacecolor=PALETTE["u_node"], markeredgecolor="white",
            markeredgewidth=1.0, zorder=22)

    crisp_text(
        ax, 0.5 * (xb0 + xb_mid), yb1 - 0.16, r"Célula $(i, j)$",
        color=PALETTE["navy_deep"], stroke_w=0.16,
        fontsize=8.4, fontweight="bold", ha="center", va="top", zorder=16,
    )
    crisp_text(
        ax, 0.5 * (xb_mid + xb1), yb1 - 0.16, r"Célula $(i+1, j)$",
        color=PALETTE["navy_deep"], stroke_w=0.16,
        fontsize=8.4, fontweight="bold", ha="center", va="top", zorder=16,
    )

    # Setas opostas de EXATA IGUAL MAGNITUDE (L = 0.94) nos dois lados da face interna!
    L_eq = 0.94
    y_arr_hi = yc_tel + 0.22
    y_arr_lo = yc_tel - 0.24

    draw_arrow(
        ax, (xb_mid - L_eq - 0.08, y_arr_hi), (xb_mid - 0.08, y_arr_hi),
        color=PALETTE["u_node"], lw=2.25, mutation_scale=11.5, zorder=20
    )
    crisp_text(
        ax, xb_mid - 0.55, y_arr_hi + 0.12,
        r"sai de $i$: $+q_{x,i+1/2,j}$",
        color=PALETTE["u_node"], stroke_w=0.15, bg_pill=PALETTE["cell_focus"], pad=0.03,
        fontsize=7.8, fontweight="bold", ha="center", va="bottom", zorder=21,
    )

    draw_arrow(
        ax, (xb_mid + L_eq + 0.08, y_arr_lo), (xb_mid + 0.08, y_arr_lo),
        color=PALETTE["z_node"], lw=2.25, mutation_scale=11.5, zorder=20
    )
    crisp_text(
        ax, xb_mid + 0.55, y_arr_lo - 0.12,
        r"entra em $i\!+\!1$: $-q_{x,i+1/2,j}$",
        color=PALETTE["z_node"], stroke_w=0.15, bg_pill=PALETTE["cell_bg"], pad=0.03,
        fontsize=7.8, fontweight="bold", ha="center", va="top", zorder=21,
    )

    # Fluxos externos nas bordas não compartilhadas (alinhados junto às setas externas)
    draw_arrow(
        ax, (xb0 - 0.26, yc_tel - 0.35), (xb0 + 0.26, yc_tel - 0.35),
        color=PALETTE["ink_muted"], lw=1.35, mutation_scale=9.0, zorder=18
    )
    crisp_text(
        ax, xb0 + 0.06, yc_tel - 0.52, r"$-q_{x,0,j}$ (borda)",
        color=PALETTE["ink_secondary"], stroke_w=0.12, bg_pill=PALETTE["cell_focus"], pad=0.03,
        fontsize=7.4, ha="left", va="top", zorder=19,
    )
    draw_arrow(
        ax, (xb1 - 0.26, yc_tel + 0.35), (xb1 + 0.26, yc_tel + 0.35),
        color=PALETTE["ink_muted"], lw=1.35, mutation_scale=9.0, zorder=18
    )
    crisp_text(
        ax, xb1 - 0.06, yc_tel + 0.52, r"$+q_{x,N_x,j}$ (borda)",
        color=PALETTE["ink_secondary"], stroke_w=0.12, bg_pill=PALETTE["cell_bg"], pad=0.03,
        fontsize=7.4, ha="right", va="bottom", zorder=19,
    )

    # Rótulo inferior de cancelamento exato na face interna (com respiro amplo abaixo de yb0)
    crisp_text(
        ax, xb_mid, -4.36,
        r"Face interna compartilhada: $\;(+q_{x,i+1/2,j}) + (-q_{x,i+1/2,j}) = 0\;$ (anulação exata)",
        color=PALETTE["u_node"], stroke_w=0.15,
        fontsize=7.95, fontweight="bold", ha="center", va="center", zorder=22,
    )

    # Divisor vertical + Identidade Global Telescópica
    ax.plot([5.08, 5.08], [-4.48, yb1 + 0.02], color=PALETTE["rule_light"], lw=0.85, zorder=6)

    x_sum = 6.73
    crisp_text(
        ax, x_sum, -2.06,
        r"Soma Global no Domínio $\Omega$:",
        color=PALETTE["navy_deep"], stroke_w=0.17,
        fontsize=8.5, fontweight="bold", ha="center", va="center", zorder=20,
    )
    crisp_text(
        ax, x_sum, -2.62,
        r"$\sum_{j,i} (D\mathbf{q})_{i,j}\,\Delta x\Delta y$",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_pill=PALETTE["panel_tint"], pad=0.10,
        fontsize=9.2, ha="center", va="center", zorder=20,
    )
    crisp_text(
        ax, x_sum, -3.28,
        r"$= \Delta y\sum_j (q_{x,N_x,j} - q_{x,0,j}) + \Delta x\sum_i (q_{y,i,N_y} - q_{y,i,0})$",
        color=PALETTE["z_node"], stroke_w=0.15,
        fontsize=8.0, fontweight="bold", ha="center", va="center", zorder=20,
    )
    crisp_text(
        ax, x_sum, -4.08,
        "Todos os fluxos internos cancelam-se;\nresta apenas o fluxo líquido pelas\n"
        + r"fronteiras externas $\partial\Omega$ (erro $\sim 10^{-16}$).",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.8, fontstyle="italic", ha="center", va="center", linespacing=1.24, zorder=20,
    )


# ---------------------------------------------------------------------------
# 6. Função Principal de Geração, Exportação e Exibição
# ---------------------------------------------------------------------------
def plot_discrete_operators_synthesis(
    output_stem="swe_discrete_operators",
    save_formats=("svg", "pdf", "png"),
    show=True,
    return_paths=False,
):
    """
    Constrói a prancha em dois painéis dos operadores discretos na malha
    escalonada de Casulli, salva/sobrescreve os arquivos vetoriais e raster em
    `../figures/` e exibe inline no notebook quando `show=True`.
    """
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
        fig, ax = plt.subplots(figsize=(16.2, 9.5), dpi=300)
        fig.patch.set_facecolor(PALETTE["bg_canvas"])
        ax.set_facecolor(PALETTE["bg_canvas"])

        # Fio vertical tracejado separando Painel Esquerdo e Painel Direito
        ax.plot([-0.12, -0.12], [-4.70, 4.66],
                color=PALETTE["rule_light"], lw=0.95, ls="--", zorder=3)

        _draw_left_panel(ax)
        _draw_right_panel(ax)

        ax.set_xlim(-8.42, 8.52)
        ax.set_ylim(-4.85, 4.82)
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
    paths = plot_discrete_operators_synthesis(show=False, return_paths=True)
    for fmt_k, p_out in paths.items():
        print(f"Saved ({fmt_k}): {p_out}")
