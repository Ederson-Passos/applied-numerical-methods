"""
Infografia científica vetorial (padrão editorial Edward Tufte / monografia de
Matemática Aplicada dos anos 80 e 90) para o encerramento da Seção 3.1:

  "COMO TRANSFORMAMOS AS EQUAÇÕES DA ÁGUA EM UM SISTEMA LINEAR?"
  Subtítulo: A estratégia de Casulli — do sistema acoplado à solução da
             elevação da superfície livre.

Segue rigorosamente a identidade visual das Figuras 1 a 12 do projeto:
  - Fundo marfim de arquivo (#FCFBF7), filetes duplos booktabs, molduras
    técnicas de cantos retos (90 graus) e ilustrações vetoriais limpas.
  - Paleta sóbria: azul-marinho, azul-petróleo, azul-claro (termos conhecidos
    em t_k) e terracota veneziano (incógnitas implícitas em t_{k+1}).
  - Tipografia LaTeX Latin Modern Roman e Computer Modern Math com reforço
    vetorial sem halo (svg.fonttype = 'path', pdf.fonttype = 42).
  - Proporção horizontal exata 16:9 em alta resolução (300 DPI).

Pode ser executado via terminal ou chamado no notebook `implementation.ipynb`:
    from generate_swe_linear_system_derivation_figure import build_figure
    build_figure()

Salva/sobrescreve automaticamente em `../figures/`:
  - swe_linear_system_derivation.svg
  - swe_linear_system_derivation.pdf
  - swe_linear_system_derivation.png
"""

import glob
import logging
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch
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
# 2. Paleta Editorial Sóbria (Marfim, Azul-Marinho, Azul-Petróleo, Azul-Claro, Terracota)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FCFBF7",       # Papel marfim muito claro (idêntico às Figuras 1–12)
    "card_bg": "#F9F7F1",         # Fundo sutil dos cartões de etapa
    "plaque_bg": "#FFFDF9",       # Fundo claro de destaque para equações centrais
    "ink_primary": "#11161C",     # Nanquim profundo para títulos e equações
    "ink_secondary": "#222B35",   # Carvão nítido para explicações
    "ink_muted": "#5C6875",       # Cinza-ardósia para notas técnicas e cotas
    "navy_deep": "#0D3149",       # Azul-marinho profundo (estrutura e cabeçalhos)
    "rule_dark": "#1E3246",       # Filetes booktabs principais
    "rule_light": "#CFC5B7",      # Divisórias internas sutis
    "petrol": "#145374",          # Azul-petróleo institucional (operadores e subtítulo)
    "teal_deep": "#17575A",       # Azul-petróleo esverdeado (componente v / recuperação)
    # Codificação semântica estrita: Azul-claro = Conhecido (t_k) | Terracota = Desconhecido (t_{k+1})
    "known_bg": "#DFEEF8",        # Azul-claro editorial para termos conhecidos
    "known_hdr": "#C7E0F2",       # Cabeçalho azul-claro
    "known_bd": "#1C5D8A",        # Borda azul-petróleo/claro nítida
    "known_ink": "#0E3B5C",       # Texto sobre fundo azul-claro
    "unk_bg": "#F9E6E1",          # Terracota suave para incógnitas futuras
    "unk_hdr": "#F2CEC5",         # Cabeçalho terracota suave
    "unk_bd": "#8E321E",          # Terracota veneziano (incógnitas em t_{k+1})
    "unk_ink": "#742312",         # Texto escuro terracota
    # Elementos físicos do corte do canal (idênticos à Figura 1)
    "water_front": "#A9CCE0",     # Coluna d'água em corte frontal
    "water_top": "#D6EAF5",       # Superfície livre oblíqua
    "water_edge": "#1E4D6B",      # Aresta da superfície livre
    "bed_front": "#C8BBAE",       # Leito sedimentar frontal
    "bed_right": "#B3A494",       # Face lateral do leito
    "bed_edge": "#5E4F41",        # Contorno geológico
    "msg_bg": "#EDF3F7",          # Faixa de síntese pedagógica de cada etapa
    "msg_bd": "#AFC4D4",          # Borda discreta da faixa de mensagem
}


def crisp_text(
    ax, x, y, s, color="#11161C", stroke_w=0.15, bg_pill=None, pad=0.08,
    border_col="none", border_lw=0.0, alpha_bg=0.96, **kwargs
):
    """Renderiza texto/equações LaTeX com micro-reforço vetorial nítido."""
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
    ax, p0, p1, color="#0D3149", lw=1.45, mutation_scale=11.5,
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
    ax, x, y, w, h, ec="#0D3149", fc="none", lw=1.05, ls="-",
    double_top=False, zorder=4
):
    """Moldura editorial clássica com cantos retos de 90 graus e duplo filete opcional."""
    ax.add_patch(Rectangle(
        (x, y), w, h,
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=zorder
    ))
    if double_top:
        ax.plot(
            [x, x + w], [y + h - 0.07, y + h - 0.07],
            color=ec, lw=0.55, zorder=zorder + 1
        )


def draw_stage_header(ax, x, y_top, w, stage_num, title_str, zorder=15):
    """Cabeçalho padronizado para cada uma das 5 etapas."""
    badge_w = 1.18
    badge_h = 0.42
    bx = x + 0.14
    by = y_top - 0.52
    ax.add_patch(Rectangle(
        (bx, by), badge_w, badge_h,
        facecolor=PALETTE["navy_deep"], edgecolor="none", zorder=zorder
    ))
    crisp_text(
        ax, bx + 0.5 * badge_w, by + 0.5 * badge_h,
        f"ETAPA {stage_num}",
        color=PALETTE["bg_canvas"], stroke_w=0.16,
        fontsize=8.3, fontweight="bold", ha="center", va="center", zorder=zorder + 1
    )
    crisp_text(
        ax, bx + badge_w + 0.16, by + 0.5 * badge_h,
        title_str,
        color=PALETTE["navy_deep"], stroke_w=0.19,
        fontsize=9.4, fontweight="bold", ha="left", va="center", zorder=zorder + 1
    )
    ax.plot(
        [x + 0.14, x + w - 0.14], [by - 0.09, by - 0.09],
        color=PALETTE["rule_light"], lw=0.80, zorder=zorder
    )


def draw_message_strip(ax, x, y, w, h, msg_str, fontsize=7.95, zorder=12):
    """Faixa inferior de síntese conceitual dentro de cada cartão."""
    ax.add_patch(Rectangle(
        (x, y), w, h,
        facecolor=PALETTE["msg_bg"], edgecolor=PALETTE["msg_bd"],
        linewidth=0.85, zorder=zorder
    ))
    ax.plot([x, x], [y, y + h], color=PALETTE["petrol"], lw=2.4, zorder=zorder + 1)
    crisp_text(
        ax, x + 0.5 * w + 0.03, y + 0.5 * h,
        msg_str,
        color=PALETTE["ink_primary"], stroke_w=0.13,
        fontsize=fontsize, fontstyle="italic",
        ha="center", va="center", linespacing=1.24, zorder=zorder + 2
    )


# ---------------------------------------------------------------------------
# 3. Ilustração Esquemática do Canal (Etapa 1) e Matriz Pentadiagonal (Etapa 5)
# ---------------------------------------------------------------------------
def draw_channel_schematic(ax, x0, y0, w, h, zorder=10):
    """
    Corte esquemático 2.5D de um canal com água exibindo com rigor geométrico:
      - Nível de referência não perturbado (z = 0, tracejado)
      - Fundo do canal (batimetria h medida de z = 0 até o leito)
      - Superfície livre ondulada (elevação z medida a partir de z = 0)
      - Profundidade total H = h + z (do fundo até a superfície livre)
      - Velocidade horizontal u, velocidade transversal/vertical no plano v e gravidade g.
    """
    xl = x0 + 0.22
    xr = x0 + w - 0.62
    dx_p, dy_p = 0.40, 0.19

    xs = np.linspace(xl, xr, 120)
    xn = (xs - xl) / (xr - xl)

    y_base = y0 + 0.07
    y_bed = y0 + 0.31 + 0.13 * (xn ** 1.4)
    y_ref = y0 + 0.99
    y_surf = y_ref + 0.26 + 0.09 * np.cos(1.60 * np.pi * xn - 0.30)

    # 1. Faixa oblíqua superior da superfície livre (2.5D)
    top_poly = (
        list(zip(xs, y_surf))
        + list(zip(xs[::-1] + dx_p, y_surf[::-1] + dy_p))
    )
    ax.add_patch(Polygon(
        top_poly, closed=True,
        facecolor=PALETTE["water_top"], edgecolor=PALETTE["water_edge"],
        linewidth=0.80, zorder=zorder + 1
    ))

    for frac in [0.38, 0.72]:
        ax.plot(
            xs + frac * dx_p, y_surf + frac * dy_p,
            color=PALETTE["petrol"], lw=0.45, alpha=0.42, zorder=zorder + 2
        )

    # 2. Face lateral direita oblíqua da água e do leito
    ax.add_patch(Polygon(
        [(xr, y_bed[-1]), (xr + dx_p, y_bed[-1] + dy_p),
         (xr + dx_p, y_surf[-1] + dy_p), (xr, y_surf[-1])],
        closed=True, facecolor="#8EB8D1", edgecolor=PALETTE["water_edge"],
        linewidth=0.80, zorder=zorder + 2
    ))
    ax.add_patch(Polygon(
        [(xr, y_base), (xr + dx_p, y_base + dy_p),
         (xr + dx_p, y_bed[-1] + dy_p), (xr, y_bed[-1])],
        closed=True, facecolor=PALETTE["bed_right"], edgecolor=PALETTE["bed_edge"],
        linewidth=0.80, zorder=zorder + 2
    ))

    # 3. Coluna d'água em corte frontal
    wat_front = (
        list(zip(xs, y_bed))
        + list(zip(xs[::-1], y_surf[::-1]))
    )
    ax.add_patch(Polygon(
        wat_front, closed=True,
        facecolor=PALETTE["water_front"], edgecolor=PALETTE["water_edge"],
        linewidth=1.05, zorder=zorder + 3
    ))

    # Curva superior destacada da superfície livre
    ax.plot(xs, y_surf, color=PALETTE["navy_deep"], lw=1.65, zorder=zorder + 6)

    # 4. Bloco geológico frontal (fundo do canal) + hachuras sedimentares
    bed_front = (
        [(xl, y_base)]
        + list(zip(xs, y_bed))
        + [(xr, y_base)]
    )
    ax.add_patch(Polygon(
        bed_front, closed=True,
        facecolor=PALETTE["bed_front"], edgecolor=PALETTE["bed_edge"],
        linewidth=1.00, zorder=zorder + 4
    ))
    for xh in np.linspace(xl + 0.22, xr - 0.22, 18):
        yh_top = np.interp(xh, xs, y_bed)
        ax.plot(
            [xh, xh - 0.10], [yh_top - 0.02, y_base + 0.04],
            color="#8A7968", lw=0.50, alpha=0.65, zorder=zorder + 5
        )

    # 5. Nível de referência z = 0 (linha tracejada limpa)
    ax.plot(
        [xl - 0.12, xr + 0.10], [y_ref, y_ref],
        color=PALETTE["rule_dark"], lw=0.88, ls="--", zorder=zorder + 6
    )
    crisp_text(
        ax, xl + 0.08, y_ref + 0.04,
        r"nível ref. ($z=0$)",
        color=PALETTE["ink_secondary"], stroke_w=0.11,
        fontsize=6.8, ha="left", va="bottom", zorder=zorder + 8
    )

    # 6. Cota da Batimetria h (entre o fundo e z = 0)
    x_h = xl + 1.48
    yb_h = float(np.interp(x_h, xs, y_bed))
    draw_arrow(
        ax, (x_h, yb_h + 0.01), (x_h, y_ref - 0.01),
        color=PALETTE["bed_edge"], lw=1.15, mutation_scale=8.5,
        arrowstyle="<|-|>", zorder=zorder + 8
    )
    crisp_text(
        ax, x_h + 0.08, 0.5 * (yb_h + y_ref),
        r"$h$",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        bg_pill=PALETTE["water_front"], pad=0.03, alpha_bg=0.90,
        fontsize=8.8, fontweight="bold", ha="left", va="center", zorder=zorder + 9
    )
    crisp_text(
        ax, x_h + 0.25, yb_h - 0.13,
        r"Fundo — batimetria ($h$)",
        color=PALETTE["bed_edge"], stroke_w=0.13,
        fontsize=7.0, fontweight="bold", ha="center", va="center", zorder=zorder + 9
    )

    # 7. Cota da Elevação da Superfície Livre z (entre z = 0 e a superfície livre)
    x_z = xl + 2.38
    ys_z = float(np.interp(x_z, xs, y_surf))
    draw_arrow(
        ax, (x_z, y_ref + 0.01), (x_z, ys_z - 0.01),
        color=PALETTE["unk_bd"], lw=1.20, mutation_scale=8.0,
        arrowstyle="<|-|>", zorder=zorder + 8
    )
    crisp_text(
        ax, x_z + 0.08, 0.5 * (y_ref + ys_z),
        r"$z$",
        color=PALETTE["unk_bd"], stroke_w=0.18,
        fontsize=8.9, fontweight="bold", ha="left", va="center", zorder=zorder + 9
    )
    # Chamada limpa estilo Tufte apontando para a superfície livre sem cruzar arestas
    x_lbl_s = xl + 1.68
    ys_pt = float(np.interp(x_lbl_s, xs, y_surf))
    ax.plot(x_lbl_s, ys_pt, marker="o", markersize=3.0, color=PALETTE["navy_deep"], zorder=zorder + 11)
    ax.plot([x_lbl_s, x_lbl_s - 0.18], [ys_pt, y0 + 1.62], color=PALETTE["petrol"], lw=0.75, zorder=zorder + 10)
    crisp_text(
        ax, x_lbl_s - 0.22, y0 + 1.62,
        r"Superfície livre ($z$)",
        color=PALETTE["petrol"], stroke_w=0.15,
        fontsize=7.35, fontweight="bold", ha="center", va="bottom", zorder=zorder + 11
    )

    # 8. Velocidade u (direção x) e velocidade v (direção y), inteiramente abaixo de y_ref!
    xu0, yu0 = xl + 3.05, y0 + 0.67
    draw_arrow(
        ax, (xu0, yu0), (xu0 + 0.90, yu0),
        color=PALETTE["navy_deep"], lw=1.55, mutation_scale=10.5, zorder=zorder + 9
    )
    crisp_text(
        ax, xu0 + 0.45, yu0 - 0.15,
        r"vel. $u$ ($x$)",
        color=PALETTE["navy_deep"], stroke_w=0.15,
        bg_pill=PALETTE["water_front"], pad=0.02, alpha_bg=0.92,
        fontsize=7.4, fontweight="bold", ha="center", va="center", zorder=zorder + 10
    )

    # Seta v colocada sobre a superfície oblíqua superior (com amplo respiro horizontal!)
    xv0 = xl + 4.82
    yv0 = float(np.interp(xv0, xs, y_surf)) + 0.05
    draw_arrow(
        ax, (xv0, yv0), (xv0 + 0.44, yv0 + 0.21),
        color=PALETTE["teal_deep"], lw=1.50, mutation_scale=10.0, zorder=zorder + 10
    )
    crisp_text(
        ax, xv0 + 0.28, yv0 + 0.25,
        r"vel. $v$ ($y$)",
        color=PALETTE["teal_deep"], stroke_w=0.15,
        fontsize=7.4, fontweight="bold", ha="center", va="bottom", zorder=zorder + 11
    )

    # 9. Gravidade g apontando verticalmente para baixo acima da superfície (com folga limpa)
    xg = xl + 3.15
    yg_bot = float(np.interp(xg, xs, y_surf)) + 0.15
    yg_top = yg_bot + 0.34
    draw_arrow(
        ax, (xg, yg_top), (xg, yg_bot),
        color=PALETTE["unk_bd"], lw=1.35, mutation_scale=9.5, zorder=zorder + 10
    )
    crisp_text(
        ax, xg + 0.10, 0.5 * (yg_top + yg_bot) + 0.02,
        r"gravidade $g$",
        color=PALETTE["unk_bd"], stroke_w=0.15,
        fontsize=7.4, fontweight="bold", ha="left", va="center", zorder=zorder + 10
    )

    # 10. Cota da Profundidade Total H = h + z (do fundo até a superfície livre)
    x_H = xr - 0.46
    yb_H = float(np.interp(x_H, xs, y_bed))
    ys_H = float(np.interp(x_H, xs, y_surf))
    draw_arrow(
        ax, (x_H, yb_H + 0.01), (x_H, ys_H - 0.01),
        color=PALETTE["navy_deep"], lw=1.35, mutation_scale=9.0,
        arrowstyle="<|-|>", zorder=zorder + 9
    )
    crisp_text(
        ax, x_H - 0.09, 0.5 * (yb_H + ys_H) - 0.08,
        r"$H = h + z$",
        color=PALETTE["navy_deep"], stroke_w=0.16,
        bg_pill=PALETTE["water_front"], pad=0.04, alpha_bg=0.95,
        fontsize=8.0, fontweight="bold", ha="right", va="center", zorder=zorder + 10
    )


def draw_pentadiagonal_system_schematic(ax, x0, y0, size=1.46, n_dim=10, zorder=12):
    """
    Desenha o sistema linear esparso esquemático:
      [ Matriz Pentadiagonal A ] . [ Vetor z^{k+1} ] = [ Vetor b^k ]
    """
    cs = size / n_dim

    # 1. Matriz esparsa A (n_dim x n_dim)
    ax.add_patch(Rectangle(
        (x0, y0), size, size,
        facecolor="#FFFFFF", edgecolor=PALETTE["navy_deep"],
        linewidth=1.15, zorder=zorder
    ))
    for k in range(1, n_dim):
        ax.plot(
            [x0 + k * cs, x0 + k * cs], [y0, y0 + size],
            color="#EBE6DC", lw=0.40, zorder=zorder + 1
        )
        ax.plot(
            [x0, x0 + size], [y0 + k * cs, y0 + k * cs],
            color="#EBE6DC", lw=0.40, zorder=zorder + 1
        )

    for r in range(n_dim):
        for c in range(n_dim):
            diff = abs(r - c)
            if diff in (0, 1, 4):
                col = (
                    PALETTE["navy_deep"] if diff == 0
                    else (PALETTE["petrol"] if diff == 1 else "#5B92B5")
                )
                pad_c = 0.10 * cs
                ax.add_patch(Rectangle(
                    (x0 + c * cs + pad_c, y0 + (n_dim - 1 - r) * cs + pad_c),
                    cs - 2 * pad_c, cs - 2 * pad_c,
                    facecolor=col, edgecolor="none", zorder=zorder + 2
                ))

    crisp_text(
        ax, x0 + 0.5 * size, y0 - 0.11,
        r"Matriz esparsa $A$" + "\n" + r"(5 diagonais)",
        color=PALETTE["navy_deep"], stroke_w=0.13,
        fontsize=7.1, fontweight="bold", ha="center", va="top",
        linespacing=1.18, zorder=zorder + 4
    )

    # Sinal de produto
    x_dot = x0 + size + 0.17
    crisp_text(
        ax, x_dot, y0 + 0.5 * size,
        r"$\cdot$",
        color=PALETTE["ink_primary"], stroke_w=0.22,
        fontsize=14.0, fontweight="bold", ha="center", va="center", zorder=zorder + 4
    )

    # 2. Vetor coluna de incógnitas z^{k+1} (Terracota)
    xv = x0 + size + 0.34
    vw = 0.28
    ax.add_patch(Rectangle(
        (xv, y0), vw, size,
        facecolor=PALETTE["unk_bg"], edgecolor=PALETTE["unk_bd"],
        linewidth=1.15, zorder=zorder + 1
    ))
    for k in range(1, n_dim):
        ax.plot(
            [xv, xv + vw], [y0 + k * cs, y0 + k * cs],
            color=PALETTE["unk_bd"], lw=0.45, alpha=0.55, zorder=zorder + 2
        )
    for k in range(n_dim):
        ax.add_patch(Rectangle(
            (xv + 0.05, y0 + k * cs + 0.04),
            vw - 0.10, cs - 0.08,
            facecolor=PALETTE["unk_bd"], alpha=0.35, edgecolor="none", zorder=zorder + 2
        ))
    crisp_text(
        ax, xv + 0.5 * vw, y0 - 0.11,
        r"$z^{k+1}$" + "\n" + r"(incóg.)",
        color=PALETTE["unk_bd"], stroke_w=0.14,
        fontsize=7.1, fontweight="bold", ha="center", va="top",
        linespacing=1.18, zorder=zorder + 4
    )

    # Sinal de igualdade
    x_eq = xv + vw + 0.21
    crisp_text(
        ax, x_eq, y0 + 0.5 * size,
        r"$=$",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=11.0, fontweight="bold", ha="center", va="center", zorder=zorder + 4
    )

    # 3. Vetor independente conhecido b^k (Azul-claro)
    xb = xv + vw + 0.42
    ax.add_patch(Rectangle(
        (xb, y0), vw, size,
        facecolor=PALETTE["known_bg"], edgecolor=PALETTE["known_bd"],
        linewidth=1.15, zorder=zorder + 1
    ))
    for k in range(1, n_dim):
        ax.plot(
            [xb, xb + vw], [y0 + k * cs, y0 + k * cs],
            color=PALETTE["known_bd"], lw=0.45, alpha=0.55, zorder=zorder + 2
        )
    for k in range(n_dim):
        ax.add_patch(Rectangle(
            (xb + 0.05, y0 + k * cs + 0.04),
            vw - 0.10, cs - 0.08,
            facecolor=PALETTE["known_bd"], alpha=0.32, edgecolor="none", zorder=zorder + 2
        ))
    crisp_text(
        ax, xb + 0.5 * vw, y0 - 0.11,
        r"$b^{k}$" + "\n" + r"(dados)",
        color=PALETTE["known_ink"], stroke_w=0.14,
        fontsize=7.1, fontweight="bold", ha="center", va="top",
        linespacing=1.18, zorder=zorder + 4
    )


# ---------------------------------------------------------------------------
# 4. Construção Principal da Prancha 16:9
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
        "COMO TRANSFORMAMOS AS EQUAÇÕES DA ÁGUA EM UM SISTEMA LINEAR?",
        color=PALETTE["navy_deep"], stroke_w=0.22,
        fontsize=13.2, fontweight="bold", ha="center", va="center", zorder=25
    )
    crisp_text(
        ax, 0.0, 5.69,
        "A estratégia de Casulli — do sistema acoplado à solução da elevação da superfície livre.",
        color=PALETTE["petrol"], stroke_w=0.15,
        fontsize=9.9, fontstyle="italic", ha="center", va="center", zorder=25
    )

    ax.plot([X_L, X_R], [5.43, 5.43], color=PALETTE["rule_dark"], lw=0.85, zorder=15)

    # =======================================================================
    # FAIXA SUPERIOR: ETAPAS 1, 2 E 3 (y = +0.62 .. +5.24)
    # =======================================================================
    Y_TOP_LO, Y_TOP_HI = 0.62, 5.24
    H_TOP = Y_TOP_HI - Y_TOP_LO

    x1, w1 = -11.66, 7.46     # [-11.66, -4.20]
    x2, w2 = -3.70, 7.20      # [-3.70,  +3.50]
    x3, w3 = 4.00, 7.66       # [+4.00, +11.66]

    # -----------------------------------------------------------------------
    # ETAPA 1 — O PROBLEMA FÍSICO
    # -----------------------------------------------------------------------
    draw_drafting_frame(
        ax, x1, Y_TOP_LO, w1, H_TOP,
        ec=PALETTE["navy_deep"], fc=PALETTE["card_bg"], lw=1.08, double_top=True
    )
    draw_stage_header(ax, x1, Y_TOP_HI, w1, 1, "O PROBLEMA FÍSICO")

    # Corte esquemático do canal (y = +2.84 .. +4.56)
    draw_channel_schematic(ax, x1 + 0.14, 2.82, w1 - 0.28, 1.72, zorder=8)

    ax.plot([x1 + 0.18, x1 + w1 - 0.18], [2.75, 2.75], color=PALETTE["rule_light"], lw=0.75, zorder=10)

    # As três equações governantes acopladas (com 'advecção' em Latin Modern Roman nítido)
    eq1_rows = [
        (2.45, "Movimento em $x$:", r"$\dfrac{\partial u}{\partial t} + \;$advecção$\; = -g\dfrac{\partial z}{\partial x} - \gamma u + \tau_x$"),
        (1.97, "Movimento em $y$:", r"$\dfrac{\partial v}{\partial t} + \;$advecção$\; = -g\dfrac{\partial z}{\partial y} - \gamma v + \tau_y$"),
        (1.49, "Continuidade:",     r"$\dfrac{\partial z}{\partial t} + \dfrac{\partial (Hu)}{\partial x} + \dfrac{\partial (Hv)}{\partial y} = 0$"),
    ]
    for y_eq, lbl_eq, math_eq in eq1_rows:
        crisp_text(
            ax, x1 + 0.22, y_eq, lbl_eq,
            color=PALETTE["petrol"], stroke_w=0.15,
            fontsize=8.05, fontweight="bold", ha="left", va="center", zorder=18
        )
        crisp_text(
            ax, x1 + 2.28, y_eq, math_eq,
            color=PALETTE["ink_primary"], stroke_w=0.15,
            fontsize=8.90, ha="left", va="center", zorder=18
        )

    # Indicador visual discreto do acoplamento mútuo (u, v <-> z) à direita das 3 equações
    x_cpl = x1 + w1 - 0.72
    draw_arrow(
        ax, (x_cpl, 2.42), (x_cpl, 1.52),
        color=PALETTE["unk_bd"], lw=1.15, mutation_scale=8.5,
        arrowstyle="<|-|>", zorder=18
    )
    crisp_text(
        ax, x_cpl + 0.10, 1.97,
        "acopladas\n" + r"$(u,v \leftrightarrow z)$",
        color=PALETTE["unk_bd"], stroke_w=0.13,
        fontsize=6.95, fontweight="bold", ha="center", va="center",
        rotation=90, linespacing=1.12, zorder=18
    )

    draw_message_strip(
        ax, x1 + 0.16, Y_TOP_LO + 0.12, w1 - 0.32, 0.50,
        "Três equações acopladas: as velocidades dependem da superfície,\n"
        "e a superfície depende das velocidades.",
        fontsize=7.80
    )

    # Seta sequencial ETAPA 1 -> ETAPA 2
    draw_arrow(
        ax, (x1 + w1 + 0.04, 2.93), (x2 - 0.04, 2.93),
        color=PALETTE["navy_deep"], lw=2.0, mutation_scale=13.5, zorder=25
    )

    # -----------------------------------------------------------------------
    # ETAPA 2 — A SEPARAÇÃO TEMPORAL
    # -----------------------------------------------------------------------
    draw_drafting_frame(
        ax, x2, Y_TOP_LO, w2, H_TOP,
        ec=PALETTE["navy_deep"], fc=PALETTE["card_bg"], lw=1.08, double_top=True
    )
    draw_stage_header(ax, x2, Y_TOP_HI, w2, 2, "A SEPARAÇÃO TEMPORAL")

    bx_k, bw_k = x2 + 0.18, 3.16
    bx_k1, bw_k1 = x2 + w2 - 0.18 - 3.16, 3.16
    by_box, bh_box = 2.40, 2.15

    # Bloco Conhecido: t = t_k (Azul-Claro)
    ax.add_patch(Rectangle(
        (bx_k, by_box), bw_k, bh_box,
        facecolor=PALETTE["known_bg"], edgecolor=PALETTE["known_bd"],
        linewidth=1.15, zorder=10
    ))
    ax.add_patch(Rectangle(
        (bx_k, by_box + bh_box - 0.52), bw_k, 0.52,
        facecolor=PALETTE["known_hdr"], edgecolor=PALETTE["known_bd"],
        linewidth=0.85, zorder=11
    ))
    crisp_text(
        ax, bx_k + 0.5 * bw_k, by_box + bh_box - 0.17,
        "INSTANTE CONHECIDO",
        color=PALETTE["navy_deep"], stroke_w=0.16,
        fontsize=7.6, fontweight="bold", ha="center", va="center", zorder=14
    )
    crisp_text(
        ax, bx_k + 0.5 * bw_k, by_box + bh_box - 0.38,
        r"$t = t_k$",
        color=PALETTE["known_ink"], stroke_w=0.17,
        fontsize=8.8, fontweight="bold", ha="center", va="center", zorder=14
    )
    crisp_text(
        ax, bx_k + 0.5 * bw_k, by_box + 1.34,
        r"• Estado e advecção: $z^k,\; F_u^k,\; F_v^k$" + "\n"
        + r"• Atrito e vento: $\gamma_u^k,\; \gamma_v^k,\; \tau_x,\; \tau_y$",
        color=PALETTE["known_ink"], stroke_w=0.13,
        fontsize=7.75, ha="center", va="center", linespacing=1.35, zorder=14
    )
    ax.add_patch(Rectangle(
        (bx_k + 0.22, by_box + 0.14), bw_k - 0.44, 0.80,
        facecolor="#F4F9FD", edgecolor=PALETTE["known_bd"],
        linewidth=0.90, zorder=12
    ))
    crisp_text(
        ax, bx_k + 0.5 * bw_k, by_box + 0.72,
        "Profundidade total conhecida:",
        color=PALETTE["petrol"], stroke_w=0.13,
        fontsize=7.3, fontweight="bold", ha="center", va="center", zorder=14
    )
    crisp_text(
        ax, bx_k + 0.5 * bw_k, by_box + 0.37,
        r"$H^k = h + z^k$",
        color=PALETTE["navy_deep"], stroke_w=0.18,
        fontsize=9.8, fontweight="bold", ha="center", va="center", zorder=14
    )

    # Seta de avanço Δt entre os dois instantes
    draw_arrow(
        ax, (bx_k + bw_k + 0.04, by_box + 1.08), (bx_k1 - 0.04, by_box + 1.08),
        color=PALETTE["navy_deep"], lw=1.55, mutation_scale=10.5, zorder=18
    )
    crisp_text(
        ax, 0.5 * (bx_k + bw_k + bx_k1), by_box + 1.24,
        r"$\Delta t$",
        color=PALETTE["navy_deep"], stroke_w=0.16,
        fontsize=8.3, fontweight="bold", ha="center", va="bottom", zorder=18
    )

    # Bloco Desconhecido: t = t_{k+1} (Terracota)
    ax.add_patch(Rectangle(
        (bx_k1, by_box), bw_k1, bh_box,
        facecolor=PALETTE["unk_bg"], edgecolor=PALETTE["unk_bd"],
        linewidth=1.15, zorder=10
    ))
    ax.add_patch(Rectangle(
        (bx_k1, by_box + bh_box - 0.52), bw_k1, 0.52,
        facecolor=PALETTE["unk_hdr"], edgecolor=PALETTE["unk_bd"],
        linewidth=0.85, zorder=11
    ))
    crisp_text(
        ax, bx_k1 + 0.5 * bw_k1, by_box + bh_box - 0.17,
        "INSTANTE DESCONHECIDO",
        color=PALETTE["unk_ink"], stroke_w=0.16,
        fontsize=7.5, fontweight="bold", ha="center", va="center", zorder=14
    )
    crisp_text(
        ax, bx_k1 + 0.5 * bw_k1, by_box + bh_box - 0.38,
        r"$t = t_{k+1}$",
        color=PALETTE["unk_bd"], stroke_w=0.17,
        fontsize=8.8, fontweight="bold", ha="center", va="center", zorder=14
    )
    crisp_text(
        ax, bx_k1 + 0.5 * bw_k1, by_box + 1.24,
        "Permanecem implícitos:",
        color=PALETTE["unk_ink"], stroke_w=0.14,
        fontsize=7.7, fontweight="bold", ha="center", va="center", zorder=14
    )
    crisp_text(
        ax, bx_k1 + 0.5 * bw_k1, by_box + 0.64,
        r"• Gradiente: $G_x z^{k+1},\; G_y z^{k+1}$" + "\n"
        + r"• Velocidades: $u^{k+1},\; v^{k+1}$" + "\n"
        + r"• Superfície futura: $z^{k+1}$",
        color=PALETTE["unk_ink"], stroke_w=0.14,
        fontsize=7.85, ha="center", va="center", linespacing=1.35, zorder=14
    )

    crisp_text(
        ax, x2 + 0.5 * w2, 1.78,
        "Os termos convectivos e os coeficientes são avaliados no instante conhecido.\n"
        "O gradiente da superfície e as velocidades permanecem implícitos.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.95, ha="center", va="center", linespacing=1.30, zorder=16
    )

    draw_message_strip(
        ax, x2 + 0.16, Y_TOP_LO + 0.12, w2 - 0.32, 0.50,
        "Transformamos os termos conhecidos em dados disponíveis\n"
        "para o próximo cálculo.",
        fontsize=7.80
    )

    # Seta sequencial ETAPA 2 -> ETAPA 3
    draw_arrow(
        ax, (x2 + w2 + 0.04, 2.93), (x3 - 0.04, 2.93),
        color=PALETTE["navy_deep"], lw=2.0, mutation_scale=13.5, zorder=25
    )

    # -----------------------------------------------------------------------
    # ETAPA 3 — ELIMINANDO AS VELOCIDADES
    # -----------------------------------------------------------------------
    draw_drafting_frame(
        ax, x3, Y_TOP_LO, w3, H_TOP,
        ec=PALETTE["navy_deep"], fc=PALETTE["card_bg"], lw=1.08, double_top=True
    )
    draw_stage_header(ax, x3, Y_TOP_HI, w3, 3, "ELIMINANDO AS VELOCIDADES")

    crisp_text(
        ax, x3 + 0.5 * w3, 4.40,
        r"Isolando $u^{k+1}$ e $v^{k+1}$ com $\alpha_u^k = (1 + \gamma_u^k\Delta t)^{-1}$ e $\alpha_v^k = (1 + \gamma_v^k\Delta t)^{-1}$:",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.85, ha="center", va="center", zorder=16
    )

    x_lhs = x3 + 0.66
    xb_part, wb_part = x3 + 1.28, 2.86
    x_minus = xb_part + wb_part + 0.24
    xt_part, wt_part = x_minus + 0.24, 2.84

    crisp_text(
        ax, xb_part + 0.5 * wb_part, 4.05,
        "PARTE AZUL: Termos conhecidos",
        color=PALETTE["known_ink"], stroke_w=0.15,
        fontsize=7.65, fontweight="bold", ha="center", va="center", zorder=18
    )
    crisp_text(
        ax, xt_part + 0.5 * wt_part, 4.05,
        "PARTE TERRACOTA: Superfície futura",
        color=PALETTE["unk_bd"], stroke_w=0.15,
        fontsize=7.65, fontweight="bold", ha="center", va="center", zorder=18
    )

    vel_rows = [
        (3.52, r"$u^{k+1} =$", r"$\alpha_u^k(F_u^k + \Delta t\,\tau_x)$", r"$g\,\Delta t\,\alpha_u^k\,G_x z^{k+1}$"),
        (2.80, r"$v^{k+1} =$", r"$\alpha_v^k(F_v^k + \Delta t\,\tau_y)$", r"$g\,\Delta t\,\alpha_v^k\,G_y z^{k+1}$"),
    ]
    for y_v, lhs_s, blue_s, terra_s in vel_rows:
        crisp_text(
            ax, x_lhs, y_v, lhs_s,
            color=PALETTE["ink_primary"], stroke_w=0.18,
            fontsize=9.8, fontweight="bold", ha="center", va="center", zorder=18
        )
        ax.add_patch(Rectangle(
            (xb_part, y_v - 0.26), wb_part, 0.52,
            facecolor=PALETTE["known_bg"], edgecolor=PALETTE["known_bd"],
            linewidth=1.05, zorder=12
        ))
        crisp_text(
            ax, xb_part + 0.5 * wb_part, y_v, blue_s,
            color=PALETTE["known_ink"], stroke_w=0.16,
            fontsize=9.35, ha="center", va="center", zorder=18
        )
        crisp_text(
            ax, x_minus, y_v, r"$-$",
            color=PALETTE["ink_primary"], stroke_w=0.20,
            fontsize=12.0, fontweight="bold", ha="center", va="center", zorder=18
        )
        ax.add_patch(Rectangle(
            (xt_part, y_v - 0.26), wt_part, 0.52,
            facecolor=PALETTE["unk_bg"], edgecolor=PALETTE["unk_bd"],
            linewidth=1.05, zorder=12
        ))
        crisp_text(
            ax, xt_part + 0.5 * wt_part, y_v, terra_s,
            color=PALETTE["unk_ink"], stroke_w=0.16,
            fontsize=9.35, ha="center", va="center", zorder=18
        )

    crisp_text(
        ax, x3 + 0.5 * w3, 2.30,
        r"$G_x, G_y$: operadores discretos de gradiente da superfície livre nas faces",
        color=PALETTE["ink_muted"], stroke_w=0.12,
        fontsize=7.35, fontstyle="italic", ha="center", va="center", zorder=16
    )

    # Seta interna apontando das equações de u^{k+1} e v^{k+1} rumo à Continuidade
    cx3 = x3 + 0.5 * w3
    draw_arrow(
        ax, (cx3, 2.13), (cx3, 1.80),
        color=PALETTE["petrol"], lw=1.55, mutation_scale=10.5, zorder=18
    )
    ax.add_patch(Rectangle(
        (cx3 - 2.55, 1.38), 5.10, 0.40,
        facecolor="#E4EFF6", edgecolor=PALETTE["petrol"],
        linewidth=1.00, zorder=14
    ))
    crisp_text(
        ax, cx3, 1.58,
        r"$\Downarrow\;$ Enviadas para a Equação da Continuidade (Etapa 4)",
        color=PALETTE["navy_deep"], stroke_w=0.15,
        fontsize=7.85, fontweight="bold", ha="center", va="center", zorder=18
    )

    # Mensagem principal da Etapa 3 alinhada perfeitamente às Etapas 1 e 2!
    draw_message_strip(
        ax, x3 + 0.16, Y_TOP_LO + 0.12, w3 - 0.32, 0.50,
        "Agora sabemos escrever as velocidades futuras\n"
        "em função da superfície futura.",
        fontsize=7.80
    )

    # =======================================================================
    # CONECTOR CONTÍNUO ETAPA 3 -> EQUAÇÃO DA CONTINUIDADE (ETAPA 4)
    # =======================================================================
    Y_BOT_LO, Y_BOT_HI = -5.24, 0.04
    H_BOT = Y_BOT_HI - Y_BOT_LO

    x4, w4 = -11.66, 11.16    # [-11.66, -0.50]
    x5, w5 = 0.06, 11.60      # [+0.06, +11.66]

    cx4 = x4 + 0.5 * w4
    y_corridor = 0.33

    ax.plot(
        [cx3, cx3, cx4, cx4],
        [Y_TOP_LO, y_corridor, y_corridor, Y_BOT_HI + 0.12],
        color=PALETTE["petrol"], lw=1.85, zorder=22
    )
    draw_arrow(
        ax, (cx4, Y_BOT_HI + 0.24), (cx4, Y_BOT_HI + 0.02),
        color=PALETTE["petrol"], lw=1.85, mutation_scale=12.5, zorder=24
    )
    crisp_text(
        ax, 1.00, y_corridor,
        r"$\longleftarrow\;$ Substituição na Continuidade: $u^{k+1}$ e $v^{k+1}$ entram na conservação discreta de massa $\;\longleftarrow$",
        color=PALETTE["petrol"], stroke_w=0.15,
        bg_pill=PALETTE["bg_canvas"], pad=0.06, border_col=PALETTE["msg_bd"], border_lw=0.75,
        fontsize=7.9, fontweight="bold", ha="center", va="center", zorder=25
    )

    # =======================================================================
    # FAIXA INFERIOR ESQUERDA: ETAPA 4 — O PASSO FUNDAMENTAL: SUBSTITUIÇÃO
    # =======================================================================
    draw_drafting_frame(
        ax, x4, Y_BOT_LO, w4, H_BOT,
        ec=PALETTE["navy_deep"], fc=PALETTE["card_bg"], lw=1.08, double_top=True
    )
    draw_stage_header(ax, x4, Y_BOT_HI, w4, 4, "O PASSO FUNDAMENTAL: SUBSTITUIÇÃO")

    # 1. Duas velocidades u^{k+1} e v^{k+1} entrando graficamente na continuidade
    u_pill_x, v_pill_x = cx4 - 2.35, cx4 + 2.35
    y_pills = -0.76

    for px_c, sym_v, expr_v in [
        (u_pill_x, r"$u^{k+1}$", r"$\alpha_u^k(F_u^k+\Delta t\tau_x) - g\Delta t\alpha_u^k G_x z^{k+1}$"),
        (v_pill_x, r"$v^{k+1}$", r"$\alpha_v^k(F_v^k+\Delta t\tau_y) - g\Delta t\alpha_v^k G_y z^{k+1}$"),
    ]:
        ax.add_patch(Rectangle(
            (px_c - 2.12, y_pills - 0.19), 4.24, 0.38,
            facecolor="#FFFFFF", edgecolor=PALETTE["petrol"], lw=0.90, zorder=12
        ))
        crisp_text(
            ax, px_c, y_pills,
            sym_v + " $=$ " + expr_v,
            color=PALETTE["ink_primary"], stroke_w=0.13,
            fontsize=7.50, ha="center", va="center", zorder=15
        )

    # Setas curvas com ângulo limpo apontando exatamente para H_u^k u^{k+1} e H_v^k v^{k+1}
    draw_arrow(
        ax, (u_pill_x + 0.55, y_pills - 0.20), (cx4 - 0.18, -1.35),
        color=PALETTE["unk_bd"], lw=1.40, mutation_scale=10.5,
        connectionstyle="arc3,rad=0.14", zorder=18
    )
    draw_arrow(
        ax, (v_pill_x - 0.35, y_pills - 0.20), (cx4 + 1.85, -1.35),
        color=PALETTE["unk_bd"], lw=1.40, mutation_scale=10.5,
        connectionstyle="arc3,rad=-0.12", zorder=18
    )

    # Placa da Equação da Continuidade Discreta
    ax.add_patch(Rectangle(
        (x4 + 0.95, -1.96), w4 - 1.90, 0.58,
        facecolor=PALETTE["plaque_bg"], edgecolor=PALETTE["rule_dark"],
        linewidth=1.05, zorder=12
    ))
    crisp_text(
        ax, cx4, -1.67,
        r"$z^{k+1} = z^k - \Delta t \left[ D_x\!\left(H_u^k u^{k+1}\right) + D_y\!\left(H_v^k v^{k+1}\right) \right]$",
        color=PALETTE["ink_primary"], stroke_w=0.17,
        fontsize=9.9, ha="center", va="center", zorder=16
    )
    crisp_text(
        ax, cx4, -2.13,
        r"$D_x, D_y$: divergência discreta dos fluxos  |  Coeficientes conhecidos: $K_u^k = H_u^k\alpha_u^k,\;\; K_v^k = H_v^k\alpha_v^k$",
        color=PALETTE["ink_muted"], stroke_w=0.12,
        fontsize=7.35, fontstyle="italic", ha="center", va="center", zorder=16
    )

    # 2. Bifurcação: separação entre Lado Esquerdo (z^{k+1}) e Lado Direito (b^k)
    bx_lhs, bw_lhs = x4 + 0.24, 5.18
    bx_rhs, bw_rhs = x4 + w4 - 0.24 - 5.18, 5.18
    by_sep, bh_sep = -3.20, 0.84

    draw_arrow(
        ax, (cx4 - 1.35, -2.23), (bx_lhs + 0.5 * bw_lhs, by_sep + bh_sep + 0.02),
        color=PALETTE["unk_bd"], lw=1.25, mutation_scale=9.5, zorder=16
    )
    draw_arrow(
        ax, (cx4 + 1.35, -2.23), (bx_rhs + 0.5 * bw_rhs, by_sep + bh_sep + 0.02),
        color=PALETTE["known_bd"], lw=1.25, mutation_scale=9.5, zorder=16
    )

    # Caixa Esquerda (Terracota): Ficam no lado esquerdo
    ax.add_patch(Rectangle(
        (bx_lhs, by_sep), bw_lhs, bh_sep,
        facecolor=PALETTE["unk_bg"], edgecolor=PALETTE["unk_bd"],
        linewidth=1.00, zorder=12
    ))
    crisp_text(
        ax, bx_lhs + 0.5 * bw_lhs, by_sep + 0.61,
        r"Dependem de $z^{k+1}$ $\rightarrow$ permanecem no lado esquerdo:",
        color=PALETTE["unk_ink"], stroke_w=0.14,
        fontsize=7.45, fontweight="bold", ha="center", va="center", zorder=15
    )
    crisp_text(
        ax, bx_lhs + 0.5 * bw_lhs, by_sep + 0.24,
        r"$z^{k+1} - g\Delta t^2\left[D_x(K_u^k G_x z^{k+1}) + D_y(K_v^k G_y z^{k+1})\right]$",
        color=PALETTE["unk_ink"], stroke_w=0.15,
        fontsize=8.25, ha="center", va="center", zorder=15
    )

    # Caixa Direita (Azul-claro): Vão para o lado direito (b^k)
    ax.add_patch(Rectangle(
        (bx_rhs, by_sep), bw_rhs, bh_sep,
        facecolor=PALETTE["known_bg"], edgecolor=PALETTE["known_bd"],
        linewidth=1.00, zorder=12
    ))
    crisp_text(
        ax, bx_rhs + 0.5 * bw_rhs, by_sep + 0.61,
        r"Termos conhecidos em $t_k$ $\rightarrow$ vão para o lado direito ($b^k$):",
        color=PALETTE["known_ink"], stroke_w=0.14,
        fontsize=7.45, fontweight="bold", ha="center", va="center", zorder=15
    )
    crisp_text(
        ax, bx_rhs + 0.5 * bw_rhs, by_sep + 0.24,
        r"$b^k = z^k - \Delta t\left[D_x(K_u^k(F_u^k+\Delta t\tau_x)) + D_y(K_v^k(F_v^k+\Delta t\tau_y))\right]$",
        color=PALETTE["known_ink"], stroke_w=0.14,
        fontsize=7.65, ha="center", va="center", zorder=15
    )

    # Setas verticais ortogonais limpas convergindo na equação resultante
    draw_arrow(
        ax, (bx_lhs + 0.5 * bw_lhs, by_sep - 0.02), (bx_lhs + 0.5 * bw_lhs, -3.52),
        color=PALETTE["unk_bd"], lw=1.25, mutation_scale=9.5, zorder=16
    )
    draw_arrow(
        ax, (bx_rhs + 0.5 * bw_rhs, by_sep - 0.02), (bx_rhs + 0.5 * bw_rhs, -3.52),
        color=PALETTE["known_bd"], lw=1.25, mutation_scale=9.5, zorder=16
    )

    # 3. Equação resultante da substituição em destaque
    draw_drafting_frame(
        ax, x4 + 0.60, -4.34, w4 - 1.20, 0.80,
        ec=PALETTE["navy_deep"], fc=PALETTE["plaque_bg"], lw=1.35, double_top=True, zorder=13
    )
    crisp_text(
        ax, cx4, -3.96,
        r"$z^{k+1} - g\,\Delta t^2 \left[ D_x\!\left(K_u^k G_x z^{k+1}\right) + D_y\!\left(K_v^k G_y z^{k+1}\right) \right] = b^k$",
        color=PALETTE["navy_deep"], stroke_w=0.19,
        fontsize=10.5, fontweight="bold", ha="center", va="center", zorder=18
    )

    # 4. Mensagem da Etapa 4
    draw_message_strip(
        ax, x4 + 0.16, Y_BOT_LO + 0.12, w4 - 0.32, 0.62,
        "Eliminamos as velocidades como incógnitas.\n"
        "Agora precisamos descobrir apenas a superfície futura.",
        fontsize=7.95
    )

    # Seta sequencial ETAPA 4 -> ETAPA 5
    draw_arrow(
        ax, (x4 + w4 + 0.04, -2.60), (x5 - 0.04, -2.60),
        color=PALETTE["navy_deep"], lw=2.1, mutation_scale=14.0, zorder=25
    )

    # =======================================================================
    # FAIXA INFERIOR DIREITA: ETAPA 5 — O SISTEMA LINEAR
    # =======================================================================
    draw_drafting_frame(
        ax, x5, Y_BOT_LO, w5, H_BOT,
        ec=PALETTE["navy_deep"], fc=PALETTE["card_bg"], lw=1.08, double_top=True
    )
    draw_stage_header(ax, x5, Y_BOT_HI, w5, 5, "O SISTEMA LINEAR")

    x_div5 = x5 + 7.12
    ax.plot([x_div5, x_div5], [Y_BOT_LO + 0.16, -0.58], color=PALETTE["rule_light"], lw=0.85, ls="--", zorder=8)

    # --- Subpainel Esquerdo da Etapa 5 ---
    xl5 = x5 + 0.22
    wl5 = 6.72
    cxl5 = xl5 + 0.5 * wl5

    # 1. Equação final em destaque
    draw_drafting_frame(
        ax, xl5, -1.84, wl5, 1.18,
        ec=PALETTE["navy_deep"], fc=PALETTE["plaque_bg"], lw=1.35, double_top=True, zorder=12
    )
    crisp_text(
        ax, cxl5, -1.02,
        r"$A\, z^{k+1} = b^k$",
        color=PALETTE["navy_deep"], stroke_w=0.22,
        fontsize=12.4, fontweight="bold", ha="center", va="center", zorder=18
    )
    crisp_text(
        ax, cxl5, -1.54,
        r"$A = I - g\,\Delta t^2 \left[ D_x K_u^k G_x + D_y K_v^k G_y \right]$",
        color=PALETTE["ink_primary"], stroke_w=0.17,
        fontsize=9.8, ha="center", va="center", zorder=18
    )

    # 2. Matriz esparsa esquemática A * z^{k+1} = b^k + notas estruturais à direita
    draw_pentadiagonal_system_schematic(ax, x0=xl5 + 0.20, y0=-3.52, size=1.46, n_dim=10, zorder=13)

    xn_m = xl5 + 3.05
    wn_m = wl5 - 3.05
    ax.add_patch(Rectangle(
        (xn_m, -3.56), wn_m, 1.50,
        facecolor="#F4F2EC", edgecolor=PALETTE["rule_light"], lw=0.85, zorder=11
    ))
    crisp_text(
        ax, xn_m + 0.14, -2.26,
        "Estrutura discreta:",
        color=PALETTE["navy_deep"], stroke_w=0.15,
        fontsize=7.9, fontweight="bold", ha="left", va="center", zorder=15
    )
    crisp_text(
        ax, xn_m + 0.14, -2.92,
        r"• $N = N_x N_y$ células acopladas" + "\n"
        + r"• Estêncil de 5 pontos ($i\pm 1,\; j\pm 1$)" + "\n"
        + r"• Contornos compatíveis ($D = -G^\top$):" + "\n"
        + r"  $A = I + g\Delta t^2(G_x^\top K_u^k G_x + G_y^\top K_v^k G_y)$",
        color=PALETTE["ink_secondary"], stroke_w=0.12,
        fontsize=7.25, ha="left", va="center", linespacing=1.34, zorder=15
    )

    # 3. Destaque do método: GRADIENTE CONJUGADO (CG)
    ax.add_patch(Rectangle(
        (xl5, Y_BOT_LO + 0.12), wl5, 1.04,
        facecolor="#E7F0F6", edgecolor=PALETTE["petrol"], lw=1.15, zorder=12
    ))
    ax.plot(
        [xl5, xl5], [Y_BOT_LO + 0.12, Y_BOT_LO + 1.16],
        color=PALETTE["navy_deep"], lw=3.0, zorder=13
    )
    crisp_text(
        ax, cxl5, Y_BOT_LO + 0.90,
        "GRADIENTE CONJUGADO (CG)",
        color=PALETTE["navy_deep"], stroke_w=0.18,
        fontsize=8.8, fontweight="bold", ha="center", va="center", zorder=16
    )
    crisp_text(
        ax, cxl5, Y_BOT_LO + 0.43,
        "Pode ser utilizado quando o operador discretizado satisfaz\n"
        "as propriedades de simetria e definição positiva.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=7.75, fontstyle="italic", ha="center", va="center",
        linespacing=1.25, zorder=16
    )

    # --- Subpainel Direito da Etapa 5: Sequência Algorítmica em 6 Passos ---
    xr5 = x_div5 + 0.20
    wr5 = (x5 + w5 - 0.20) - xr5
    cxr5 = xr5 + 0.5 * wr5

    steps_seq = [
        ("SUPERFÍCIE ATUAL",                 PALETTE["known_bg"], PALETTE["known_bd"], PALETTE["known_ink"]),
        ("MONTAGEM DO SISTEMA LINEAR",       "#F3F0E8",           PALETTE["rule_dark"], PALETTE["ink_primary"]),
        (r"RESOLUÇÃO DE  $A z = b$",         "#E2EEF5",           PALETTE["navy_deep"], PALETTE["navy_deep"]),
        ("NOVA SUPERFÍCIE",                  PALETTE["unk_bg"],   PALETTE["unk_bd"],   PALETTE["unk_ink"]),
        ("RECUPERAÇÃO DAS VELOCIDADES",      "#E4F0EE",           PALETTE["teal_deep"], PALETTE["teal_deep"]),
        ("PRÓXIMO INSTANTE DE TEMPO",        "#EDF2F6",           PALETTE["navy_deep"], PALETTE["navy_deep"]),
    ]
    bh_s = 0.48
    gap_s = 0.28
    y_top_s = -0.66

    for idx_s, (txt_s, fc_s, ec_s, tc_s) in enumerate(steps_seq):
        ys_top = y_top_s - idx_s * (bh_s + gap_s)
        ys_bot = ys_top - bh_s
        ax.add_patch(Rectangle(
            (xr5, ys_bot), wr5, bh_s,
            facecolor=fc_s, edgecolor=ec_s,
            linewidth=1.18 if idx_s in (2, 3) else 0.95, zorder=13
        ))
        crisp_text(
            ax, cxr5, ys_bot + 0.5 * bh_s,
            txt_s,
            color=tc_s, stroke_w=0.16,
            fontsize=7.65, fontweight="bold", ha="center", va="center", zorder=16
        )
        if idx_s < len(steps_seq) - 1:
            draw_arrow(
                ax, (cxr5, ys_bot - 0.02), (cxr5, ys_bot - gap_s + 0.02),
                color=PALETTE["navy_deep"], lw=1.35, mutation_scale=9.5, zorder=18
            )

    # Seta pontilhada sutil ligando o quadro do CG à etapa "RESOLUÇÃO DE A z = b"
    y_cg_link_target = y_top_s - 2 * (bh_s + gap_s) - 0.5 * bh_s
    draw_arrow(
        ax, (xl5 + wl5 + 0.02, Y_BOT_LO + 0.64), (xr5 - 0.02, y_cg_link_target),
        color=PALETTE["petrol"], lw=1.10, ls=":", mutation_scale=9.0,
        connectionstyle="arc3,rad=-0.18", zorder=19
    )

    # =======================================================================
    # RODAPÉ — A IDEIA CENTRAL (Faixa Editorial em Destaque + Duplo Filete)
    # =======================================================================
    y_foot, h_foot = -6.38, 0.90
    w_badge_f = 3.25

    ax.add_patch(Rectangle(
        (X_L, y_foot), X_R - X_L, h_foot,
        facecolor="#EDF3F8", edgecolor=PALETTE["navy_deep"],
        linewidth=1.25, zorder=14
    ))
    ax.add_patch(Rectangle(
        (X_L, y_foot), w_badge_f, h_foot,
        facecolor=PALETTE["navy_deep"], edgecolor=PALETTE["navy_deep"],
        linewidth=1.25, zorder=15
    ))
    crisp_text(
        ax, X_L + 0.5 * w_badge_f, y_foot + 0.5 * h_foot,
        "A IDEIA CENTRAL",
        color=PALETTE["bg_canvas"], stroke_w=0.19,
        fontsize=9.8, fontweight="bold", ha="center", va="center", zorder=18
    )
    crisp_text(
        ax, 0.5 * (X_L + w_badge_f + X_R), y_foot + 0.5 * h_foot,
        "Não resolvemos simultaneamente as três incógnitas. Eliminamos as velocidades,\n"
        "resolvemos primeiro a superfície livre e depois recuperamos as velocidades.",
        color=PALETTE["navy_deep"], stroke_w=0.17,
        fontsize=9.55, fontweight="bold", fontstyle="italic",
        ha="center", va="center", linespacing=1.26, zorder=18
    )

    # Fechamento inferior booktabs
    ax.plot([X_L, X_R], [-6.53, -6.53], color=PALETTE["rule_dark"], lw=0.60, zorder=15)
    ax.plot([X_L, X_R], [-6.62, -6.62], color=PALETTE["rule_dark"], lw=1.50, zorder=15)

    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = FIGURES_DIR / "swe_linear_system_derivation.svg"
    pdf_path = FIGURES_DIR / "swe_linear_system_derivation.pdf"
    png_path = FIGURES_DIR / "swe_linear_system_derivation.png"

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
