"""
Pacote `analysis` — Análises estatísticas e visualizações de resultados do
trabalho computacional de Águas Rasas 2D (Casulli, 1990).

Princípios arquiteturais deste pacote:
  1. Recarregamento dinâmico transparente (`importlib.reload`): qualquer edição
     nos scripts internos deste pacote reflete imediatamente na reexecução da
     célula do notebook, sem exigir reinicialização do Kernel.
  2. Persistência e sobrescrita automática: toda visualização chamada a partir
     do notebook grava e sobrescreve automaticamente seus arquivos (`.png`,
     `.svg`, `.pdf`) em `docs/computational_work/figures/results/`.
"""

import importlib
from . import style as _style
from . import tidal_forcing as _tidal_forcing
from .style import RESULTS_FIGURES_DIR, PALETTE_RESULTS, save_result_figure


def plot_tidal_boundary_forcing(*args, **kwargs):
    """
    Recarrega os módulos de estilo e visualização a partir do disco e executa
    `tidal_forcing.plot_tidal_boundary_forcing`, garantindo que modificações na
    função sobrescrevam imediatamente as imagens em `figures/results/`.
    """
    importlib.reload(_style)
    importlib.reload(_tidal_forcing)
    return _tidal_forcing.plot_tidal_boundary_forcing(*args, **kwargs)


__all__ = [
    "RESULTS_FIGURES_DIR",
    "PALETTE_RESULTS",
    "save_result_figure",
    "plot_tidal_boundary_forcing",
]
