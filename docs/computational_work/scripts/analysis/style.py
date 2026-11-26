"""
Utilitários compartilhados de estilo editorial (Edward Tufte / monografias
científicas dos anos 80 e 90) e persistência automática para todas as análises
estatísticas e visualizações de resultados geradas a partir do notebook.

Princípio de persistência:
  Toda figura de análise/resultado gerada no notebook é salva e sobrescrita
  automaticamente em `docs/computational_work/figures/results/` a cada execução.
"""

import glob
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patheffects as pe

# Silencia avisos internos do fontTools sobre cabeçalhos OpenType do MiKTeX
logging.getLogger("fontTools").setLevel(logging.ERROR)

for _fp in glob.glob(r"C:\Program Files\MiKTeX*\fonts\opentype\public\lm\lmroman*.otf"):
    fm.fontManager.addfont(_fp)
HAS_LM_ROMAN = any(f.name == "Latin Modern Roman" for f in fm.fontManager.ttflist)

# Subpasta dedicada exclusivamente às imagens de gráficos/resultados do notebook
RESULTS_FIGURES_DIR = Path(__file__).resolve().parent.parent.parent / "figures" / "results"

PALETTE_RESULTS = {
    "bg_canvas": "#FAF8F3",       # Papel creme/marfim editorial
    "panel_bg": "#FCFBF7",        # Interior dos eixos de dados
    "legend_bg": "#F5F1E9",       # Fundo sóbrio para legendas e quadros booktabs
    "ink_primary": "#11161C",     # Nanquim profundo para títulos e equações
    "ink_secondary": "#283648",   # Azul-ardósia escuro para eixos, bordas e texto
    "ink_muted": "#626E7A",       # Cinza técnico para grades sutis e cotas
    "grid_line": "#D8D0C4",       # Grade pontilhada discreta estilo anos 80
    "navy_deep": "#0D3149",       # Azul-prussiano (curvas principais e canal)
    "cerulean": "#145374",        # Azul-cerúleo (preamar / enchente)
    "water_fill": "#B8D6E8",      # Preenchimento translúcido de coluna d'água / enchente
    "water_deep": "#7FAEC9",      # Coluna d'água profunda no canal
    "teal_mid": "#17575A",        # Verde-petróleo (nível médio / marcos intermediários)
    "terracotta": "#8E321E",      # Terracota veneziano (baixa-mar / vazante / paredes)
    "ebb_fill": "#E8CEC4",        # Preenchimento suave de vazante (z < 0)
    "amber_acc": "#A86518",       # Âmbar seco (recorte de zoom / fronteira aberta)
    "bed_fill": "#CFC3B4",        # Leito sedimentar em corte geológico
    "bed_edge": "#5E4F41",        # Contorno batimétrico
    "bed_hatch": "#827161",       # Hachura geológica oblíqua clássica
    "wall_shade": "#E6E0D6",      # Sombreado sutil de parede impermeável fechada
}


def rc_tufte_context():
    """Retorna o dicionário rcParams padrão da série para `plt.rc_context`."""
    return {
        "font.family": "Latin Modern Roman" if HAS_LM_ROMAN else "serif",
        "mathtext.fontset": "cm",
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "axes.unicode_minus": True,
        "figure.facecolor": PALETTE_RESULTS["bg_canvas"],
        "savefig.facecolor": PALETTE_RESULTS["bg_canvas"],
    }


def style_tufte_axes(ax, grid=True):
    """Aplica moldura técnica nítida, marcas externas e grade discreta estilo anos 80/90."""
    ax.set_facecolor(PALETTE_RESULTS["panel_bg"])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE_RESULTS["ink_secondary"])
        spine.set_linewidth(0.90)
    ax.tick_params(
        colors=PALETTE_RESULTS["ink_secondary"],
        labelsize=8.7,
        direction="out",
        length=3.5,
        width=0.80,
    )
    if grid:
        ax.grid(
            True,
            linestyle=":",
            linewidth=0.65,
            color=PALETTE_RESULTS["ink_muted"],
            alpha=0.38,
            zorder=0,
        )


def set_crisp_title(ax, title_str, loc="left", pad=7, fontsize=10.0, color=None):
    """Define título de eixo com micro-reforço vetorial nas hastes finas."""
    if color is None:
        color = PALETTE_RESULTS["navy_deep"]
    t_obj = ax.set_title(
        title_str, loc=loc, pad=pad, fontsize=fontsize, fontweight="bold", color=color
    )
    t_obj.set_path_effects([pe.withStroke(linewidth=0.14, foreground=color)])
    return t_obj


def save_result_figure(fig, output_stem, save_formats=("png", "svg", "pdf"), dpi=300):
    """
    Salva e sobrescreve incondicionalmente a figura na subpasta
    `docs/computational_work/figures/results/` a cada execução.
    """
    RESULTS_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    saved_paths = {}
    for fmt in save_formats:
        out_path = RESULTS_FIGURES_DIR / f"{output_stem}.{fmt}"
        save_kw = dict(
            format=fmt,
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
        )
        if fmt.lower() == "png":
            save_kw["dpi"] = dpi
        fig.savefig(out_path, **save_kw)
        saved_paths[fmt] = out_path
    return saved_paths
