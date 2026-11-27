"""
Ilustração científica vetorial (padrão editorial Edward Tufte / monografia de
Matemática Aplicada dos anos 80 e 90) para o encerramento da Seção 3.2.3
("Estêncil de cinco pontos"):

  "DO ESTÊNCIL DE CINCO PONTOS À MATRIZ ESPARSA PENTADIAGONAL"
  Subtítulo: Formação do coeficiente central a_P, interação exclusiva com as
             quatro vizinhas ortogonais e estrutura de no máximo cinco não nulos por linha.

Segue rigorosamente a identidade visual das Figuras 1 a 13 do projeto:
  - Fundo marfim de arquivo (#FCFBF7), filetes duplos booktabs, molduras
    técnicas de cantos retos (90 graus) e diagramas vetoriais limpos.
  - Codificação semântica consistente com toda a Seção 2 e 3:
      * Azul-petróleo / marinho (#145374 / #0D3149): célula central (i,j) e a_P
      * Terracota veneziano (#8E321E): faces verticais K_u e vizinhas Leste/Oeste (a_E, a_W)
      * Verde-petróleo (#17575A): faces horizontais K_v e vizinhas Norte/Sul (a_N, a_S)
      * Âmbar seco (#9C5E14): termo identidade (+1)
  - Tipografia LaTeX Latin Modern Roman e Computer Modern Math convertida em
    curvas vetoriais exatas (svg.fonttype = 'path', pdf.fonttype = 42).
  - Proporção horizontal exata 16:9 em alta resolução (300 DPI).

Salva/sobrescreve automaticamente em `../figures/`:
  - swe_five_point_stencil.svg
  - swe_five_point_stencil.pdf
  - swe_five_point_stencil.png
"""

import glob
import logging
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, Circle
import matplotlib.patheffects as pe

logging.getLogger("fontTools").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# 1. Tipografia LaTeX (Latin Modern Roman + Computer Modern Math)
# ---------------------------------------------------------------------------
for _fp in glob.glob(r"C:\Program Files\MiKTeX*\fonts\opentype\public\lm\lmroman*.otf"):
    fm.fontManager.addfont(_fp)
_HAS_LM = any(f.name == "Latin Modern Roman" for f in fm.fontManager.ttflist)

plt.rcParams.update({
    "font.family": "Latin Modern Roman" if _HAS_LM else "serif",
    "mathtext.fontset": "cm",
    "svg.fonttype": "path",
    "pdf.fonttype": 42,
    "axes.unicode_minus": True,
})

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

# ---------------------------------------------------------------------------
# 2. Paleta Editorial Sóbria (Idêntica às Figuras 1–13)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FCFBF7",       # Papel marfim muito claro
    "card_bg": "#F9F7F1",         # Fundo sutil dos painéis
    "plaque_bg": "#FFFDF9",       # Fundo claro de placas matemáticas
    "ink_primary": "#11161C",     # Nanquim profundo
    "ink_secondary": "#222B35",   # Carvão nítido
    "ink_muted": "#66727E",       # Cinza-ardósia para zeros e cotas
    "navy_deep": "#0D3149",       # Azul-marinho estrutural
    "rule_dark": "#1E3246",       # Filetes booktabs
    "rule_light": "#CFC5B7",      # Divisórias sutis
    # Cores semânticas da malha escalonada e das diagonais
    "p_col": "#145374",           # Azul-petróleo: centro (i,j) e diagonal principal a_P
    "p_bg": "#DCECF7",            # Fundo da célula central (i,j)
    "ew_col": "#8E321E",          # Terracota: faces verticais K_u e vizinhas E/W (a_E, a_W)
    "ew_bg": "#F9E6E1",           # Fundo das células Leste e Oeste
    "ns_col": "#17575A",          # Verde-petróleo: faces horizontais K_v e vizinhas N/S (a_N, a_S)
    "ns_bg": "#E3F1EF",           # Fundo das células Norte e Sul
    "id_col": "#9C5E14",          # Âmbar seco: parcela do termo identidade (+1)
    "id_bg": "#FBF0DC",           # Fundo suave do bloco identidade (+1)
    "zero_bg": "#F3EFE8",         # Células não acopladas na malha 2D
    "zero_bd": "#B8AFA2",         # Borda tracejada/sutil de células com peso 0
    "row_hi": "#FFF6DF",          # Faixa suave destacando a Linha p na matriz A
    "msg_bg": "#EDF3F8",          # Faixa de síntese
    "msg_bd": "#AFC4D4",          # Borda discreta
}


def crisp_text(
    ax, x, y, s, color="#11161C", stroke_w=0.15, bg_pill=None, pad=0.07,
    border_col="none", border_lw=0.0, alpha_bg=0.95, **kwargs
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
    ax, p0, p1, color="#0D3149", lw=1.40, mutation_scale=11.0,
    arrowstyle="-|>", zorder=20, ls="-", connectionstyle="arc3,rad=0.0"
):
    arr = FancyArrowPatch(
        p0, p1,
        arrowstyle=arrowstyle,
        mutation_scale=mutation_scale,
        color=color,
        linewidth=lw,
        linestyle=ls,
        connectionstyle=connectionstyle,
        shrinkA=0,
        shrinkB=0,
        zorder=zorder,
    )
    ax.add_patch(arr)
    return arr


def draw_drafting_frame(
    ax, x, y, w, h, ec="#0D3149", fc="none", lw=1.08, ls="-",
    double_top=False, zorder=4
):
    ax.add_patch(Rectangle(
        (x, y), w, h,
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=zorder
    ))
    if double_top:
        ax.plot(
            [x, x + w], [y + h - 0.07, y + h - 0.07],
            color=ec, lw=0.55, zorder=zorder + 1
        )


def draw_panel_header(ax, x, y_top, w, num_str, title_str, zorder=15):
    badge_w = 0.56
    badge_h = 0.42
    bx = x + 0.14
    by = y_top - 0.53
    ax.add_patch(Rectangle(
        (bx, by), badge_w, badge_h,
        facecolor=PALETTE["navy_deep"], edgecolor="none", zorder=zorder
    ))
    crisp_text(
        ax, bx + 0.5 * badge_w, by + 0.5 * badge_h,
        num_str,
        color=PALETTE["bg_canvas"], stroke_w=0.17,
        fontsize=8.8, fontweight="bold", ha="center", va="center", zorder=zorder + 1
    )
    crisp_text(
        ax, bx + badge_w + 0.14, by + 0.5 * badge_h,
        title_str,
        color=PALETTE["navy_deep"], stroke_w=0.19,
        fontsize=9.1, fontweight="bold", ha="left", va="center", zorder=zorder + 1
    )
    ax.plot(
        [x + 0.14, x + w - 0.14], [by - 0.09, by - 0.09],
        color=PALETTE["rule_light"], lw=0.80, zorder=zorder
    )


def draw_mini_stencil_icon(ax, cx, cy, cs=0.28, active_dirs=("E", "W", "N", "S"), zorder=14):
    """Desenha um mini-ícone 3x3 mostrando quantos vizinhos ativos restam (5, 4 ou 3)."""
    offsets = {
        "P": (0, 0, PALETTE["p_bg"], PALETTE["p_col"]),
        "E": (1, 0, PALETTE["ew_bg"], PALETTE["ew_col"]),
        "W": (-1, 0, PALETTE["ew_bg"], PALETTE["ew_col"]),
        "N": (0, 1, PALETTE["ns_bg"], PALETTE["ns_col"]),
        "S": (0, -1, PALETTE["ns_bg"], PALETTE["ns_col"]),
    }
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            ax.add_patch(Rectangle(
                (cx + (dx - 0.5) * cs, cy + (dy - 0.5) * cs), cs, cs,
                facecolor="#F2EFE8", edgecolor="#CCC4B8", lw=0.55, zorder=zorder
            ))
    # Desenha ativos
    for key in ("P",) + tuple(active_dirs):
        dx, dy, fc, ec = offsets[key]
        ax.add_patch(Rectangle(
            (cx + (dx - 0.5) * cs, cy + (dy - 0.5) * cs), cs, cs,
            facecolor=fc, edgecolor=ec, lw=1.05, zorder=zorder + 2
        ))
        ax.plot(
            cx + dx * cs, cy + dy * cs,
            marker="o", markersize=2.8, color=ec, zorder=zorder + 3
        )


# ---------------------------------------------------------------------------
# 3. Construção Principal da Prancha 16:9
# ---------------------------------------------------------------------------
def build_figure(show=False, return_paths=False):
    # Proporção estritamente 16:9 (19.2 x 10.8 pol, viewBox 24.0 x 13.5)
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    X_MIN, X_MAX = -12.00, 12.00
    Y_MIN, Y_MAX = -6.75, 6.75
    X_L, X_R = -11.66, 11.66

    # =======================================================================
    # CABEÇALHO EDITORIAL (Booktabs Double Rule + Título e Subtítulo)
    # =======================================================================
    ax.plot([X_L, X_R], [6.54, 6.54], color=PALETTE["rule_dark"], lw=1.50, zorder=15)
    ax.plot([X_L, X_R], [6.45, 6.45], color=PALETTE["rule_dark"], lw=0.60, zorder=15)

    crisp_text(
        ax, 0.0, 6.08,
        "DO ESTÊNCIL DE CINCO PONTOS À MATRIZ ESPARSA PENTADIAGONAL",
        color=PALETTE["navy_deep"], stroke_w=0.22,
        fontsize=13.2, fontweight="bold", ha="center", va="center", zorder=25
    )
    crisp_text(
        ax, 0.0, 5.69,
        r"Formação de $a_P$ pelo termo identidade e pelas quatro vizinhas — produzindo uma matriz esparsa com no máximo cinco não nulos por linha.",
        color=PALETTE["p_col"], stroke_w=0.15,
        fontsize=9.75, fontstyle="italic", ha="center", va="center", zorder=25
    )

    ax.plot([X_L, X_R], [5.43, 5.43], color=PALETTE["rule_dark"], lw=0.85, zorder=15)

    # Coordenadas dos 3 painéis principais (y = -5.20 .. +5.22)
    Y_P_LO, Y_P_HI = -5.20, 5.22
    H_P = Y_P_HI - Y_P_LO

    x1, w1 = -11.66, 7.56     # [-11.66, -4.10]
    x2, w2 = -3.62, 6.84      # [-3.62,  +3.22]
    x3, w3 = 3.70, 7.96       # [+3.70, +11.66]

    # =======================================================================
    # PAINEL 1: INTERAÇÃO LOCAL NA MALHA ESCALONADA (ESTÊNCIL DE 5 PONTOS)
    # =======================================================================
    draw_drafting_frame(
        ax, x1, Y_P_LO, w1, H_P,
        ec=PALETTE["navy_deep"], fc=PALETTE["card_bg"], lw=1.08, double_top=True
    )
    draw_panel_header(ax, x1, Y_P_HI, w1, "1", "INTERAÇÃO LOCAL: ESTÊNCIL DE 5 PONTOS")

    cx1 = x1 + 0.5 * w1

    # --- Malha 5x5 centrada em (i, j) com margens laterais amplas para chamadas ---
    cs = 0.80
    gx0 = cx1 - 2.5 * cs
    gy0 = 0.16

    stencil_map = {
        (2, 2): ("P", PALETTE["p_bg"], PALETTE["p_col"], r"$z_{i,j}$", r"$a_P$"),
        (3, 2): ("E", PALETTE["ew_bg"], PALETTE["ew_col"], r"$z_{i+1,j}$", r"$a_E$"),
        (1, 2): ("W", PALETTE["ew_bg"], PALETTE["ew_col"], r"$z_{i-1,j}$", r"$a_W$"),
        (2, 3): ("N", PALETTE["ns_bg"], PALETTE["ns_col"], r"$z_{i,j+1}$", r"$a_N$"),
        (2, 1): ("S", PALETTE["ns_bg"], PALETTE["ns_col"], r"$z_{i,j-1}$", r"$a_S$"),
    }

    for ix in range(5):
        for iy in range(5):
            xc = gx0 + ix * cs
            yc = gy0 + iy * cs
            if (ix, iy) in stencil_map:
                tag, fc, ec, z_lbl, a_lbl = stencil_map[(ix, iy)]
                ax.add_patch(Rectangle(
                    (xc, yc), cs, cs,
                    facecolor=fc, edgecolor=ec, linewidth=1.65, zorder=10
                ))
                # Ponto central da célula
                ax.plot(
                    xc + 0.5 * cs, yc + 0.66 * cs,
                    marker="o", markersize=5.0, color=ec, zorder=14
                )
                crisp_text(
                    ax, xc + 0.5 * cs, yc + 0.44 * cs,
                    z_lbl,
                    color=PALETTE["ink_primary"], stroke_w=0.15,
                    fontsize=8.2, fontweight="bold", ha="center", va="center", zorder=15
                )
                crisp_text(
                    ax, xc + 0.5 * cs, yc + 0.17 * cs,
                    a_lbl,
                    color=ec, stroke_w=0.17,
                    fontsize=8.8, fontweight="bold", ha="center", va="center", zorder=15
                )
            else:
                ax.add_patch(Rectangle(
                    (xc, yc), cs, cs,
                    facecolor=PALETTE["zero_bg"], edgecolor=PALETTE["zero_bd"],
                    linewidth=0.70, linestyle="--", zorder=6
                ))
                crisp_text(
                    ax, xc + 0.5 * cs, yc + 0.5 * cs,
                    r"$0$",
                    color=PALETTE["ink_muted"], stroke_w=0.10,
                    fontsize=8.2, ha="center", va="center", zorder=8
                )

    # Rótulos de colunas (i-2 .. i+2) no topo e linhas (j-2 .. j+2) na base/esquerda sutil
    col_lbls = [r"$i-2$", r"$i-1$", r"$i$", r"$i+1$", r"$i+2$"]
    row_lbls = [r"$j-2$", r"$j-1$", r"$j$", r"$j+1$", r"$j+2$"]
    for idx_c, cl in enumerate(col_lbls):
        col_c = PALETTE["p_col"] if idx_c == 2 else (PALETTE["ew_col"] if idx_c in (1, 3) else PALETTE["ink_muted"])
        crisp_text(
            ax, gx0 + (idx_c + 0.5) * cs, gy0 + 5 * cs + 0.10, cl,
            color=col_c, stroke_w=0.13, fontsize=7.6, fontweight="bold",
            ha="center", va="bottom", zorder=15
        )
    for idx_r, rl in enumerate(row_lbls):
        col_r = PALETTE["p_col"] if idx_r == 2 else (PALETTE["ns_col"] if idx_r in (1, 3) else PALETTE["ink_muted"])
        crisp_text(
            ax, gx0 - 0.10, gy0 + (idx_r + 0.5) * cs, rl,
            color=col_r, stroke_w=0.13, fontsize=7.5, fontweight="bold",
            ha="right", va="center", zorder=15
        )

    # Condutâncias nas 4 faces compartilhadas + setas de acoplamento
    x_c_mid = gx0 + 2.5 * cs
    y_c_mid = gy0 + 2.5 * cs

    # Faces Leste (i+1/2, j) e Oeste (i-1/2, j)
    for x_face in [gx0 + 3.0 * cs, gx0 + 2.0 * cs]:
        ax.plot(
            [x_face, x_face], [gy0 + 2.08 * cs, gy0 + 2.92 * cs],
            color=PALETTE["ew_col"], lw=3.0, zorder=16
        )
        ax.plot(
            x_face, y_c_mid + 0.20 * cs,
            marker="s", markersize=5.0, markerfacecolor=PALETTE["ew_col"],
            markeredgecolor="white", markeredgewidth=0.7, zorder=18
        )

    draw_arrow(
        ax, (gx0 + 2.74 * cs, y_c_mid + 0.20 * cs), (gx0 + 3.26 * cs, y_c_mid + 0.20 * cs),
        color=PALETTE["ew_col"], lw=1.15, mutation_scale=7.8, arrowstyle="<|-|>", zorder=17
    )
    draw_arrow(
        ax, (gx0 + 1.74 * cs, y_c_mid + 0.20 * cs), (gx0 + 2.26 * cs, y_c_mid + 0.20 * cs),
        color=PALETTE["ew_col"], lw=1.15, mutation_scale=7.8, arrowstyle="<|-|>", zorder=17
    )

    # Faces Norte (i, j+1/2) e Sul (i, j-1/2)
    for y_face in [gy0 + 3.0 * cs, gy0 + 2.0 * cs]:
        ax.plot(
            [gx0 + 2.08 * cs, gx0 + 2.92 * cs], [y_face, y_face],
            color=PALETTE["ns_col"], lw=3.0, zorder=16
        )
        ax.plot(
            x_c_mid, y_face,
            marker="D", markersize=4.8, markerfacecolor=PALETTE["ns_col"],
            markeredgecolor="white", markeredgewidth=0.7, zorder=18
        )

    # Chamadas externas 100% fora da malha 5x5 (nas margens laterais esquerda e direita!)
    # Margem direita: K_{v,i,j+1/2} (alto) e K_{u,i+1/2,j} (meio)
    xr_call = gx0 + 5.0 * cs + 0.16
    ax.plot(
        [x_c_mid + 0.18 * cs, gx0 + 5.0 * cs + 0.12],
        [gy0 + 3.0 * cs, gy0 + 3.95 * cs],
        color=PALETTE["ns_col"], lw=0.85, zorder=19
    )
    crisp_text(
        ax, xr_call, gy0 + 3.95 * cs,
        r"$K_{v,i,j+\frac{1}{2}}$",
        color=PALETTE["ns_col"], stroke_w=0.15,
        bg_pill="#FFFFFF", pad=0.04, border_col=PALETTE["ns_col"], border_lw=0.65,
        fontsize=7.45, fontweight="bold", ha="left", va="center", zorder=20
    )

    ax.plot(
        [gx0 + 3.0 * cs, gx0 + 5.0 * cs + 0.12],
        [gy0 + 2.78 * cs, gy0 + 2.85 * cs],
        color=PALETTE["ew_col"], lw=0.85, zorder=19
    )
    crisp_text(
        ax, xr_call, gy0 + 2.85 * cs,
        r"$K_{u,i+\frac{1}{2},j}$",
        color=PALETTE["ew_col"], stroke_w=0.15,
        bg_pill="#FFFFFF", pad=0.04, border_col=PALETTE["ew_col"], border_lw=0.65,
        fontsize=7.45, fontweight="bold", ha="left", va="center", zorder=20
    )

    ax.plot(
        [x_c_mid + 0.18 * cs, gx0 + 5.0 * cs + 0.12],
        [gy0 + 2.0 * cs, gy0 + 1.05 * cs],
        color=PALETTE["ns_col"], lw=0.85, zorder=19
    )
    crisp_text(
        ax, xr_call, gy0 + 1.05 * cs,
        r"$K_{v,i,j-\frac{1}{2}}$",
        color=PALETTE["ns_col"], stroke_w=0.15,
        bg_pill="#FFFFFF", pad=0.04, border_col=PALETTE["ns_col"], border_lw=0.65,
        fontsize=7.45, fontweight="bold", ha="left", va="center", zorder=20
    )

    # Margem esquerda (acima de j+2 / ao lado de j+2): K_{u,i-1/2,j}
    xl_call = gx0 - 0.56
    ax.plot(
        [gx0 + 2.0 * cs, xl_call + 0.04],
        [gy0 + 2.78 * cs, gy0 + 3.95 * cs],
        color=PALETTE["ew_col"], lw=0.85, zorder=19
    )
    crisp_text(
        ax, xl_call, gy0 + 3.95 * cs,
        r"$K_{u,i-\frac{1}{2},j}$",
        color=PALETTE["ew_col"], stroke_w=0.15,
        bg_pill="#FFFFFF", pad=0.04, border_col=PALETTE["ew_col"], border_lw=0.65,
        fontsize=7.45, fontweight="bold", ha="right", va="center", zorder=20
    )

    # Cotas Δx e Δy discretas
    draw_arrow(
        ax, (gx0, gy0 - 0.18), (gx0 + cs, gy0 - 0.18),
        color=PALETTE["ink_secondary"], lw=0.95, mutation_scale=7.5, arrowstyle="<|-|>", zorder=16
    )
    crisp_text(
        ax, gx0 + 0.5 * cs, gy0 - 0.33, r"$\Delta x$",
        color=PALETTE["ink_secondary"], stroke_w=0.13, fontsize=7.6, ha="center", va="center", zorder=16
    )
    crisp_text(
        ax, gx0 + 3.0 * cs, gy0 - 0.25,
        r"Células com $0$: sem face comum com $(i,j)$",
        color=PALETTE["ink_muted"], stroke_w=0.11, fontsize=7.2, fontstyle="italic",
        ha="center", va="center", zorder=16
    )

    # --- Equação do operador local e fórmulas dos 4 vizinhos ---
    ax.plot([x1 + 0.18, x1 + w1 - 0.18], [-0.46, -0.46], color=PALETTE["rule_light"], lw=0.80, zorder=10)

    draw_drafting_frame(
        ax, x1 + 0.22, -1.52, w1 - 0.44, 0.92,
        ec=PALETTE["navy_deep"], fc=PALETTE["plaque_bg"], lw=1.15, double_top=True, zorder=12
    )
    crisp_text(
        ax, cx1, -0.86,
        r"$(Az)_{i,j} = a_P z_{i,j} + a_E z_{i+1,j} + a_W z_{i-1,j} + a_N z_{i,j+1} + a_S z_{i,j-1}$",
        color=PALETTE["ink_primary"], stroke_w=0.17,
        fontsize=8.95, fontweight="bold", ha="center", va="center", zorder=16
    )
    crisp_text(
        ax, cx1, -1.30,
        "Ação do operador linear sobre a célula $(i,j)$: soma ponderada de apenas 5 nós",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.3, fontstyle="italic", ha="center", va="center", zorder=16
    )

    # Duas caixas lado a lado para os 4 coeficientes das células vizinhas
    bw_c = 0.5 * (w1 - 0.60)
    bx_ew = x1 + 0.22
    bx_ns = bx_ew + bw_c + 0.16
    by_c, bh_c = -3.98, 2.28

    # Caixa Leste / Oeste (Faces verticais K_u)
    ax.add_patch(Rectangle(
        (bx_ew, by_c), bw_c, bh_c,
        facecolor=PALETTE["ew_bg"], edgecolor=PALETTE["ew_col"], lw=1.05, zorder=11
    ))
    crisp_text(
        ax, bx_ew + 0.5 * bw_c, by_c + bh_c - 0.24,
        "Vizinhas Leste e Oeste (faces $x$)",
        color=PALETTE["ew_col"], stroke_w=0.15,
        fontsize=7.65, fontweight="bold", ha="center", va="center", zorder=15
    )
    crisp_text(
        ax, bx_ew + 0.5 * bw_c, by_c + 1.38,
        r"$a_E = -\dfrac{g\,\Delta t^2}{\Delta x^2}\,K_{u,i+\frac{1}{2},j}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=8.55, ha="center", va="center", zorder=15
    )
    crisp_text(
        ax, bx_ew + 0.5 * bw_c, by_c + 0.55,
        r"$a_W = -\dfrac{g\,\Delta t^2}{\Delta x^2}\,K_{u,i-\frac{1}{2},j}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=8.55, ha="center", va="center", zorder=15
    )

    # Caixa Norte / Sul (Faces horizontais K_v)
    ax.add_patch(Rectangle(
        (bx_ns, by_c), bw_c, bh_c,
        facecolor=PALETTE["ns_bg"], edgecolor=PALETTE["ns_col"], lw=1.05, zorder=11
    ))
    crisp_text(
        ax, bx_ns + 0.5 * bw_c, by_c + bh_c - 0.24,
        "Vizinhas Norte e Sul (faces $y$)",
        color=PALETTE["ns_col"], stroke_w=0.15,
        fontsize=7.65, fontweight="bold", ha="center", va="center", zorder=15
    )
    crisp_text(
        ax, bx_ns + 0.5 * bw_c, by_c + 1.38,
        r"$a_N = -\dfrac{g\,\Delta t^2}{\Delta y^2}\,K_{v,i,j+\frac{1}{2}}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=8.55, ha="center", va="center", zorder=15
    )
    crisp_text(
        ax, bx_ns + 0.5 * bw_c, by_c + 0.55,
        r"$a_S = -\dfrac{g\,\Delta t^2}{\Delta y^2}\,K_{v,i,j-\frac{1}{2}}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=8.55, ha="center", va="center", zorder=15
    )

    # Faixa inferior do Painel 1
    ax.add_patch(Rectangle(
        (x1 + 0.22, Y_P_LO + 0.16), w1 - 0.44, 0.90,
        facecolor=PALETTE["msg_bg"], edgecolor=PALETTE["msg_bd"], lw=0.85, zorder=11
    ))
    ax.plot([x1 + 0.22, x1 + 0.22], [Y_P_LO + 0.16, Y_P_LO + 1.06], color=PALETTE["p_col"], lw=2.5, zorder=12)
    crisp_text(
        ax, cx1 + 0.03, Y_P_LO + 0.61,
        r"Como $K_u, K_v \geq 0$, todos os pesos vizinhos são não positivos ($a_E, a_W, a_N, a_S \leq 0$)" + "\n"
        + "e medem o acoplamento difusivo-gravitacional através das 4 faces da célula.",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.45, fontstyle="italic", ha="center", va="center", linespacing=1.26, zorder=14
    )

    # Seta Painel 1 -> Painel 2
    draw_arrow(
        ax, (x1 + w1 + 0.04, 0.0), (x2 - 0.04, 0.0),
        color=PALETTE["navy_deep"], lw=2.0, mutation_scale=13.5, zorder=25
    )

    # =======================================================================
    # PAINEL 2: FORMAÇÃO DO COEFICIENTE CENTRAL a_P (IDENTIDADE + 4 VIZINHAS)
    # =======================================================================
    draw_drafting_frame(
        ax, x2, Y_P_LO, w2, H_P,
        ec=PALETTE["navy_deep"], fc=PALETTE["card_bg"], lw=1.08, double_top=True
    )
    draw_panel_header(ax, x2, Y_P_HI, w2, "2", r"FORMAÇÃO DO COEFICIENTE CENTRAL $a_P$")

    cx2 = x2 + 0.5 * w2

    # 1. Placa da fórmula central a_P = 1 - a_E - a_W - a_N - a_S
    draw_drafting_frame(
        ax, x2 + 0.22, 3.16, w2 - 0.44, 1.34,
        ec=PALETTE["p_col"], fc=PALETTE["plaque_bg"], lw=1.30, double_top=True, zorder=12
    )
    crisp_text(
        ax, cx2, 4.04,
        r"$a_P = 1 - a_E - a_W - a_N - a_S$",
        color=PALETTE["navy_deep"], stroke_w=0.21,
        fontsize=11.4, fontweight="bold", ha="center", va="center", zorder=16
    )
    crisp_text(
        ax, cx2, 3.46,
        r"Como $a_E, a_W, a_N, a_S \leq 0$:"
        + r"$\quad a_P = 1 + |a_E| + |a_W| + |a_N| + |a_S| \geq 1$",
        color=PALETTE["p_col"], stroke_w=0.15,
        fontsize=8.35, fontweight="bold", ha="center", va="center", zorder=16
    )

    # 2. Diagrama Visual de Decomposição em Barras (Identidade + 4 Vizinhas = Dominância Diagonal!)
    ax.add_patch(Rectangle(
        (x2 + 0.22, 0.22), w2 - 0.44, 2.74,
        facecolor="#FFFFFF", edgecolor=PALETTE["rule_light"], lw=0.95, zorder=10
    ))
    crisp_text(
        ax, cx2, 2.72,
        r"Composição geométrica de $a_P$ e dominância diagonal estrita:",
        color=PALETTE["navy_deep"], stroke_w=0.15,
        fontsize=8.0, fontweight="bold", ha="center", va="center", zorder=14
    )

    # Coordenadas das barras empilhadas
    bar_x0 = x2 + 0.52
    segs = [
        (1.18, PALETTE["id_bg"], PALETTE["id_col"], r"$+1$", "Identidade ($I$)"),
        (1.12, PALETTE["ew_bg"], PALETTE["ew_col"], r"$|a_E|$", ""),
        (1.12, PALETTE["ew_bg"], PALETTE["ew_col"], r"$|a_W|$", ""),
        (1.18, PALETTE["ns_bg"], PALETTE["ns_col"], r"$|a_N|$", ""),
        (1.18, PALETTE["ns_bg"], PALETTE["ns_col"], r"$|a_S|$", ""),
    ]
    total_bar_w = sum(s[0] for s in segs)  # 5.78

    # Barra Superior: a_P completo
    y_b1, h_b = 1.82, 0.52
    cur_x = bar_x0
    for sw, sfc, sec, slbl, _ in segs:
        ax.add_patch(Rectangle(
            (cur_x, y_b1), sw, h_b,
            facecolor=sfc, edgecolor=sec, lw=1.15, zorder=13
        ))
        crisp_text(
            ax, cur_x + 0.5 * sw, y_b1 + 0.5 * h_b, slbl,
            color=sec, stroke_w=0.17, fontsize=8.6, fontweight="bold",
            ha="center", va="center", zorder=15
        )
        cur_x += sw

    crisp_text(
        ax, bar_x0, y_b1 + h_b + 0.13,
        r"Diagonal principal $a_P$ (célula central):",
        color=PALETTE["p_col"], stroke_w=0.14,
        fontsize=7.55, fontweight="bold", ha="left", va="center", zorder=15
    )

    # Barra Inferior: soma dos módulos das 4 vizinhas (alinhada à direita de +1!)
    y_b2 = 0.92
    cur_x2 = bar_x0 + segs[0][0]
    for sw, sfc, sec, slbl, _ in segs[1:]:
        ax.add_patch(Rectangle(
            (cur_x2, y_b2), sw, h_b,
            facecolor=sfc, edgecolor=sec, lw=1.00, alpha=0.82, zorder=13
        ))
        crisp_text(
            ax, cur_x2 + 0.5 * sw, y_b2 + 0.5 * h_b, slbl,
            color=sec, stroke_w=0.15, fontsize=8.2,
            ha="center", va="center", zorder=15
        )
        cur_x2 += sw

    # Cota destacando a margem exata "+1" de dominância diagonal!
    draw_arrow(
        ax, (bar_x0, y_b2 + 0.5 * h_b), (bar_x0 + segs[0][0] - 0.02, y_b2 + 0.5 * h_b),
        color=PALETTE["id_col"], lw=1.35, mutation_scale=8.5, arrowstyle="<|-|>", zorder=16
    )
    crisp_text(
        ax, bar_x0 + 0.5 * segs[0][0], y_b2 + 0.5 * h_b + 0.16,
        r"folga $= 1$",
        color=PALETTE["id_col"], stroke_w=0.15,
        fontsize=7.4, fontweight="bold", ha="center", va="center", zorder=16
    )
    crisp_text(
        ax, bar_x0 + segs[0][0], y_b2 + h_b + 0.13,
        r"Soma dos módulos das 4 vizinhas ($|a_E|+|a_W|+|a_N|+|a_S|$):",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.35, ha="left", va="center", zorder=15
    )

    # Propriedade algébrica resultante na base do quadro branco (duas linhas arejadas)
    crisp_text(
        ax, cx2, 0.56,
        r"Estrita dominância diagonal: $|a_P| - (|a_E|+|a_W|+|a_N|+|a_S|) = 1 > 0$" + "\n"
        + r"Soma algébrica da linha em célula interna: $a_P + a_E + a_W + a_N + a_S = 1$",
        color=PALETTE["navy_deep"], stroke_w=0.13,
        fontsize=7.20, fontweight="bold", ha="center", va="center",
        linespacing=1.28, zorder=15
    )

    # 3. Por que "no máximo cinco coeficientes não nulos"? (Interna vs. Borda vs. Canto)
    ax.add_patch(Rectangle(
        (x2 + 0.22, -3.98), w2 - 0.44, 4.00,
        facecolor="#F4F1EA", edgecolor=PALETTE["rule_light"], lw=0.90, zorder=10
    ))
    crisp_text(
        ax, cx2, -0.26,
        "Por que cada linha possui NO MÁXIMO 5 não nulos?",
        color=PALETTE["navy_deep"], stroke_w=0.16,
        fontsize=8.2, fontweight="bold", ha="center", va="center", zorder=15
    )
    crisp_text(
        ax, cx2, -0.62,
        "O número exato de coeficientes não nulos na linha depende da posição da célula:",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.35, ha="center", va="center", zorder=15
    )

    cases_x = [x2 + 1.25, cx2, x2 + w2 - 1.25]
    cases_info = [
        (("E", "W", "N", "S"), "Célula Interna", "5 não nulos", r"$a_P, a_E, a_W, a_N, a_S$"),
        (("E", "W", "N"),      "Borda Fechada",  "4 não nulos", r"ex.: Sul ($a_S = 0$)"),
        (("E", "N"),           "Canto Fechado",  "3 não nulos", r"ex.: SO ($a_W = a_S = 0$)"),
    ]
    for xc_i, (dirs_i, title_i, cnt_i, sub_i) in zip(cases_x, cases_info):
        ax.add_patch(Rectangle(
            (xc_i - 0.96, -3.76), 1.92, 2.86,
            facecolor="#FFFFFF", edgecolor=PALETTE["msg_bd"], lw=0.85, zorder=12
        ))
        crisp_text(
            ax, xc_i, -1.14, title_i,
            color=PALETTE["navy_deep"], stroke_w=0.15,
            fontsize=7.65, fontweight="bold", ha="center", va="center", zorder=15
        )
        draw_mini_stencil_icon(ax, xc_i, -2.02, cs=0.34, active_dirs=dirs_i, zorder=14)
        ax.add_patch(Rectangle(
            (xc_i - 0.78, -3.14), 1.56, 0.38,
            facecolor=PALETTE["p_bg"] if len(dirs_i) == 4 else "#EDF3F7",
            edgecolor=PALETTE["p_col"], lw=0.80, zorder=14
        ))
        crisp_text(
            ax, xc_i, -2.95, cnt_i,
            color=PALETTE["navy_deep"], stroke_w=0.16,
            fontsize=7.8, fontweight="bold", ha="center", va="center", zorder=16
        )
        crisp_text(
            ax, xc_i, -3.48, sub_i,
            color=PALETTE["ink_muted"], stroke_w=0.11,
            fontsize=7.0, ha="center", va="center", zorder=15
        )

    # Faixa inferior do Painel 2
    ax.add_patch(Rectangle(
        (x2 + 0.22, Y_P_LO + 0.16), w2 - 0.44, 0.90,
        facecolor=PALETTE["msg_bg"], edgecolor=PALETTE["msg_bd"], lw=0.85, zorder=11
    ))
    ax.plot([x2 + 0.22, x2 + 0.22], [Y_P_LO + 0.16, Y_P_LO + 1.06], color=PALETTE["id_col"], lw=2.5, zorder=12)
    crisp_text(
        ax, cx2 + 0.03, Y_P_LO + 0.61,
        r"Mesmo quando uma face vizinha se anula na fronteira ($K = 0$), a fórmula" + "\n"
        + r"$a_P = 1 - a_E - a_W - a_N - a_S$ ajusta automaticamente o peso central.",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.45, fontstyle="italic", ha="center", va="center", linespacing=1.26, zorder=14
    )

    # Seta Painel 2 -> Painel 3
    draw_arrow(
        ax, (x2 + w2 + 0.04, 0.0), (x3 - 0.04, 0.0),
        color=PALETTE["navy_deep"], lw=2.0, mutation_scale=13.5, zorder=25
    )

    # =======================================================================
    # PAINEL 3: MATRIZ ESPARSA PENTADIAGONAL (MÁX. 5 NÃO NULOS POR LINHA)
    # =======================================================================
    draw_drafting_frame(
        ax, x3, Y_P_LO, w3, H_P,
        ec=PALETTE["navy_deep"], fc=PALETTE["card_bg"], lw=1.08, double_top=True
    )
    draw_panel_header(ax, x3, Y_P_HI, w3, "3", "MATRIZ ESPARSA: MÁX. 5 NÃO NULOS / LINHA")

    cx3 = x3 + 0.5 * w3

    # --- Matriz real 16 x 16 para malha 4 x 4 (N_x = 4, N_y = 4 -> N = 16) ---
    nx_m, ny_m = 4, 4
    n_tot = nx_m * ny_m  # 16
    m_size = 4.00
    mcs = m_size / n_tot  # 0.25
    mx0 = x3 + 0.78
    my0 = 0.28

    crisp_text(
        ax, mx0 + 0.5 * m_size, my0 + m_size + 0.14,
        r"Matriz global $A \in \mathrm{I\!R}^{N\times N}$ (ilustração $4\times 4 \Rightarrow N=16$)",
        color=PALETTE["navy_deep"], stroke_w=0.15,
        fontsize=7.85, fontweight="bold", ha="center", va="bottom", zorder=18
    )

    # Fundo branco da matriz (representando os zeros!)
    ax.add_patch(Rectangle(
        (mx0, my0), m_size, m_size,
        facecolor="#FFFFFF", edgecolor=PALETTE["navy_deep"], lw=1.20, zorder=10
    ))

    # Linha destacada p = 5 -> célula interna (i=1, j=1) em numeração 0..3!
    # Seus vizinhos exatos em 4x4: S=(1,0)->1, W=(0,1)->4, P=(1,1)->5, E=(2,1)->6, N=(1,2)->9!
    p_row = 5
    y_prow = my0 + (n_tot - 1 - p_row) * mcs
    ax.add_patch(Rectangle(
        (mx0, y_prow), m_size, mcs,
        facecolor=PALETTE["row_hi"], edgecolor=PALETTE["id_col"],
        linewidth=1.10, zorder=11
    ))

    # Grade interna finíssima da matriz 16x16 + blocos 4x4
    for k in range(1, n_tot):
        lw_g = 0.65 if k % nx_m == 0 else 0.32
        col_g = "#C8BFB2" if k % nx_m == 0 else "#ECE7DF"
        ax.plot([mx0 + k * mcs, mx0 + k * mcs], [my0, my0 + m_size], color=col_g, lw=lw_g, zorder=11)
        ax.plot([mx0, mx0 + m_size], [my0 + k * mcs, my0 + k * mcs], color=col_g, lw=lw_g, zorder=11)

    # Preenchimento matematicamente exato da matriz pentadiagonal 2D em malha 4x4!
    for r in range(n_tot):
        ir, jr = r % nx_m, r // nx_m
        neighbors = [
            (r, PALETTE["p_col"]),
        ]
        if ir > 0:
            neighbors.append((r - 1, PALETTE["ew_col"]))
        if ir < nx_m - 1:
            neighbors.append((r + 1, PALETTE["ew_col"]))
        if jr > 0:
            neighbors.append((r - nx_m, PALETTE["ns_col"]))
        if jr < ny_m - 1:
            neighbors.append((r + nx_m, PALETTE["ns_col"]))

        for c, col_entry in neighbors:
            pad_e = 0.08 * mcs if r == p_row else 0.14 * mcs
            ax.add_patch(Rectangle(
                (mx0 + c * mcs + pad_e, my0 + (n_tot - 1 - r) * mcs + pad_e),
                mcs - 2 * pad_e, mcs - 2 * pad_e,
                facecolor=col_entry, edgecolor="none",
                alpha=1.0 if r == p_row else 0.86, zorder=13
            ))

    # Indicador lateral "Linha p" à esquerda da matriz
    crisp_text(
        ax, mx0 - 0.08, y_prow + 0.5 * mcs,
        r"Linha $p$",
        color=PALETTE["id_col"], stroke_w=0.16,
        fontsize=7.6, fontweight="bold", ha="right", va="center", zorder=18
    )

    # Produto por z = b ao lado direito da matriz
    x_dot3 = mx0 + m_size + 0.18
    crisp_text(
        ax, x_dot3, my0 + 0.5 * m_size, r"$\cdot$",
        color=PALETTE["ink_primary"], stroke_w=0.22, fontsize=14.0,
        ha="center", va="center", zorder=16
    )

    xv3 = x_dot3 + 0.18
    vw3 = 0.30
    ax.add_patch(Rectangle(
        (xv3, my0), vw3, m_size,
        facecolor="#FAF7F2", edgecolor=PALETTE["navy_deep"], lw=1.10, zorder=11
    ))
    active_cols_p = {1: PALETTE["ns_bg"], 4: PALETTE["ew_bg"], 5: PALETTE["p_bg"], 6: PALETTE["ew_bg"], 9: PALETTE["ns_bg"]}
    active_bds_p = {1: PALETTE["ns_col"], 4: PALETTE["ew_col"], 5: PALETTE["p_col"], 6: PALETTE["ew_col"], 9: PALETTE["ns_col"]}
    for k in range(n_tot):
        yk = my0 + (n_tot - 1 - k) * mcs
        if k in active_cols_p:
            ax.add_patch(Rectangle(
                (xv3, yk), vw3, mcs,
                facecolor=active_cols_p[k], edgecolor=active_bds_p[k], lw=0.95, zorder=13
            ))
        elif k > 0:
            ax.plot([xv3, xv3 + vw3], [yk + mcs, yk + mcs], color="#E5DFD5", lw=0.35, zorder=12)

    crisp_text(
        ax, xv3 + 0.5 * vw3, my0 + m_size + 0.14, r"$z$",
        color=PALETTE["navy_deep"], stroke_w=0.17, fontsize=8.8, fontweight="bold",
        ha="center", va="bottom", zorder=18
    )

    # Legenda compacta das 5 diagonais à direita do vetor z
    xl_diag = xv3 + vw3 + 0.26
    wr_diag = (x3 + w3 - 0.20) - xl_diag
    ax.add_patch(Rectangle(
        (xl_diag, my0 + 0.55), wr_diag, m_size - 0.55,
        facecolor="#F4F1EA", edgecolor=PALETTE["rule_light"], lw=0.85, zorder=10
    ))
    crisp_text(
        ax, xl_diag + 0.5 * wr_diag, my0 + m_size - 0.24,
        "As 5 Diagonais\nNão Nulas de $A$:",
        color=PALETTE["navy_deep"], stroke_w=0.15,
        fontsize=7.65, fontweight="bold", ha="center", va="center", linespacing=1.22, zorder=15
    )

    diag_items = [
        (my0 + 2.86, PALETTE["p_col"],  r"Diag. $0$: $a_P$",      "centro $(i,j)$"),
        (my0 + 2.18, PALETTE["ew_col"], r"Diag. $\pm 1$: $a_W,a_E$", "vizinhas O / L"),
        (my0 + 1.50, PALETTE["ns_col"], r"Diag. $\pm N_x$: $a_S,a_N$", "vizinhas S / N"),
        (my0 + 0.86, "#FFFFFF",         r"Branco $= 0$",          "sem interação"),
    ]
    for yd, cd, t1, t2 in diag_items:
        ax.add_patch(Rectangle(
            (xl_diag + 0.12, yd - 0.08), 0.20, 0.20,
            facecolor=cd, edgecolor=PALETTE["navy_deep"] if cd == "#FFFFFF" else cd,
            lw=0.80, zorder=14
        ))
        crisp_text(
            ax, xl_diag + 0.40, yd + 0.05, t1,
            color=PALETTE["ink_primary"], stroke_w=0.14,
            fontsize=7.25, fontweight="bold", ha="left", va="center", zorder=15
        )
        crisp_text(
            ax, xl_diag + 0.40, yd - 0.15, t2,
            color=PALETTE["ink_muted"], stroke_w=0.10,
            fontsize=6.75, ha="left", va="center", zorder=15
        )

    # --- Zoom da Linha p (mostrando explicitamente os 5 não nulos e os 11 zeros!) ---
    yz_row = -1.16
    hz_row = 0.44
    wz_tot = w3 - 0.48
    xz0 = x3 + 0.24
    wcs = wz_tot / n_tot

    # Guia ortogonal de ampliação saindo da Linha p sem cruzar o vetor z nem a legenda!
    ax.plot(
        [mx0, xz0],
        [y_prow, yz_row + hz_row],
        color=PALETTE["id_col"], lw=0.80, ls="--", zorder=12
    )
    ax.plot(
        [mx0 + m_size, mx0 + m_size, xz0 + wz_tot],
        [y_prow, my0 - 0.12, yz_row + hz_row],
        color=PALETTE["id_col"], lw=0.80, ls="--", zorder=12
    )

    crisp_text(
        ax, cx3, yz_row + hz_row + 0.22,
        r"Ampliação da Linha $p$ — Célula interna $(i,j)$: exatamente 5 coeficientes não nulos e $N - 5$ zeros",
        color=PALETTE["navy_deep"], stroke_w=0.15,
        bg_pill=PALETTE["card_bg"], pad=0.03,
        fontsize=7.55, fontweight="bold", ha="center", va="center", zorder=18
    )

    row_p_spec = {
        1: (PALETTE["ns_bg"], PALETTE["ns_col"], r"$a_S$"),
        4: (PALETTE["ew_bg"], PALETTE["ew_col"], r"$a_W$"),
        5: (PALETTE["p_bg"],  PALETTE["p_col"],  r"$a_P$"),
        6: (PALETTE["ew_bg"], PALETTE["ew_col"], r"$a_E$"),
        9: (PALETTE["ns_bg"], PALETTE["ns_col"], r"$a_N$"),
    }
    for c in range(n_tot):
        xc_z = xz0 + c * wcs
        if c in row_p_spec:
            fc_z, ec_z, lbl_z = row_p_spec[c]
            ax.add_patch(Rectangle(
                (xc_z, yz_row), wcs, hz_row,
                facecolor=fc_z, edgecolor=ec_z, lw=1.35, zorder=15
            ))
            crisp_text(
                ax, xc_z + 0.5 * wcs, yz_row + 0.5 * hz_row, lbl_z,
                color=ec_z, stroke_w=0.17, fontsize=8.3, fontweight="bold",
                ha="center", va="center", zorder=17
            )
        else:
            ax.add_patch(Rectangle(
                (xc_z, yz_row), wcs, hz_row,
                facecolor="#FFFFFF", edgecolor="#CFC7BA", lw=0.65, zorder=13
            ))
            crisp_text(
                ax, xc_z + 0.5 * wcs, yz_row + 0.5 * hz_row, r"$0$",
                color=PALETTE["ink_muted"], stroke_w=0.10, fontsize=7.6,
                ha="center", va="center", zorder=14
            )

    crisp_text(
        ax, xz0 + 1.5 * wcs, yz_row - 0.18, r"$p - N_x$",
        color=PALETTE["ns_col"], stroke_w=0.12, fontsize=6.9, fontweight="bold", ha="center", va="center", zorder=16
    )
    crisp_text(
        ax, xz0 + 5.5 * wcs, yz_row - 0.18, r"$p-1,\; p,\; p+1$",
        color=PALETTE["p_col"], stroke_w=0.12, fontsize=6.9, fontweight="bold", ha="center", va="center", zorder=16
    )
    crisp_text(
        ax, xz0 + 9.5 * wcs, yz_row - 0.18, r"$p + N_x$",
        color=PALETTE["ns_col"], stroke_w=0.12, fontsize=6.9, fontweight="bold", ha="center", va="center", zorder=16
    )

    # --- Consequência Quantitativa de Esparsidade nas Malhas de Casulli ---
    ax.add_patch(Rectangle(
        (x3 + 0.24, -3.98), w3 - 0.48, 2.40,
        facecolor="#FFFFFF", edgecolor=PALETTE["rule_light"], lw=0.95, zorder=11
    ))
    crisp_text(
        ax, cx3, -1.84,
        "Consequência computacional nas malhas de referência de Casulli:",
        color=PALETTE["navy_deep"], stroke_w=0.15,
        fontsize=8.0, fontweight="bold", ha="center", va="center", zorder=15
    )

    # Duas barras comparativas de esparsidade (Malha Grossa vs Malha Fina)
    sparsity_rows = [
        (-2.52, "Malha Grossa ($40 \\times 20 \\Rightarrow N = 800$):",
         r"$\leq 5$ não nulos / $800$ colunas  $\longrightarrow$  $\mathbf{99{,}38\%}$ de zeros ($< 4\,000$ vs. $640\,000$ entradas)", 0.045),
        (-3.40, "Malha Fina ($120 \\times 60 \\Rightarrow N = 7\,200$):",
         r"$\leq 5$ não nulos / $7\,200$ colunas  $\longrightarrow$  $\mathbf{99{,}93\%}$ de zeros ($< 36\,000$ vs. $51{,}84\times 10^6$ entradas)", 0.018),
    ]
    bx_sp = x3 + 0.48
    bw_sp = w3 - 0.96
    for y_sp, title_sp, desc_sp, nz_frac_vis in sparsity_rows:
        crisp_text(
            ax, bx_sp, y_sp + 0.28, title_sp,
            color=PALETTE["p_col"], stroke_w=0.14,
            fontsize=7.55, fontweight="bold", ha="left", va="center", zorder=15
        )
        # Barra visual proporcional (com fração mínima visível à esquerda em azul-marinho e resto em marfim = zeros)
        ax.add_patch(Rectangle(
            (bx_sp, y_sp - 0.06), bw_sp, 0.20,
            facecolor="#F3EFE8", edgecolor="#C5BCB0", lw=0.75, zorder=13
        ))
        ax.add_patch(Rectangle(
            (bx_sp, y_sp - 0.06), bw_sp * nz_frac_vis, 0.20,
            facecolor=PALETTE["p_col"], edgecolor=PALETTE["navy_deep"], lw=0.75, zorder=14
        ))
        crisp_text(
            ax, bx_sp + bw_sp * nz_frac_vis + 0.14, y_sp + 0.04, desc_sp,
            color=PALETTE["ink_secondary"], stroke_w=0.12,
            fontsize=7.05, ha="left", va="center", zorder=15
        )

    # Faixa inferior do Painel 3
    ax.add_patch(Rectangle(
        (x3 + 0.24, Y_P_LO + 0.16), w3 - 0.48, 0.90,
        facecolor=PALETTE["msg_bg"], edgecolor=PALETTE["msg_bd"], lw=0.85, zorder=11
    ))
    ax.plot([x3 + 0.24, x3 + 0.24], [Y_P_LO + 0.16, Y_P_LO + 1.06], color=PALETTE["navy_deep"], lw=2.5, zorder=12)
    crisp_text(
        ax, cx3 + 0.03, Y_P_LO + 0.61,
        "Armazenar apenas as 5 diagonais (DIA/CSR) ou avaliar o estêncil Matrix-Free\n"
        r"reduz o custo por iteração de $\mathcal{O}(N^2)$ para $\mathcal{O}(N)$.",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.45, fontstyle="italic", ha="center", va="center", linespacing=1.26, zorder=14
    )

    # =======================================================================
    # RODAPÉ — SÍNTESE DO RESULTADO FUNDAMENTAL (Seção 3.2.3)
    # =======================================================================
    y_foot, h_foot = -6.36, 0.92
    w_badge_f = 3.55

    ax.add_patch(Rectangle(
        (X_L, y_foot), X_R - X_L, h_foot,
        facecolor=PALETTE["msg_bg"], edgecolor=PALETTE["navy_deep"],
        linewidth=1.25, zorder=14
    ))
    ax.add_patch(Rectangle(
        (X_L, y_foot), w_badge_f, h_foot,
        facecolor=PALETTE["navy_deep"], edgecolor=PALETTE["navy_deep"],
        linewidth=1.25, zorder=15
    ))
    crisp_text(
        ax, X_L + 0.5 * w_badge_f, y_foot + 0.5 * h_foot,
        "RESULTADO ESTRUTURAL",
        color=PALETTE["bg_canvas"], stroke_w=0.19,
        fontsize=9.4, fontweight="bold", ha="center", va="center", zorder=18
    )
    crisp_text(
        ax, 0.5 * (X_L + w_badge_f + X_R), y_foot + 0.5 * h_foot,
        r"O termo identidade e os quatro pesos vizinhos determinam $a_P = 1 - a_E - a_W - a_N - a_S$; como cada célula" + "\n"
        "interage apenas com suas quatro vizinhas imediatas, cada linha de $A$ possui, no máximo, cinco coeficientes não nulos.",
        color=PALETTE["navy_deep"], stroke_w=0.16,
        fontsize=9.2, fontweight="bold", fontstyle="italic",
        ha="center", va="center", linespacing=1.26, zorder=18
    )

    # Fechamento inferior booktabs
    ax.plot([X_L, X_R], [-6.52, -6.52], color=PALETTE["rule_dark"], lw=0.60, zorder=15)
    ax.plot([X_L, X_R], [-6.61, -6.61], color=PALETTE["rule_dark"], lw=1.50, zorder=15)

    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = FIGURES_DIR / "swe_five_point_stencil.svg"
    pdf_path = FIGURES_DIR / "swe_five_point_stencil.pdf"
    png_path = FIGURES_DIR / "swe_five_point_stencil.png"

    fig.savefig(svg_path, format="svg", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, facecolor=fig.get_facecolor())

    if show:
        plt.show()
    plt.close(fig)

    paths = {"svg": svg_path, "pdf": pdf_path, "png": png_path}
    if return_paths:
        return paths
    for fmt, p in paths.items():
        print(f"Saved ({fmt}): {p}")


if __name__ == "__main__":
    build_figure()
