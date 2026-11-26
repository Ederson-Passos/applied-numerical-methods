"""
Pacote `tests` — Verificações de consistência geométrica, exatidão discreta,
conservação telescópica e condições de contorno (Casulli, 1990).
"""

from .test_velocity_boundary_conditions import test_velocity_boundary_conditions
from .test_tidal_forcing import test_tidal_forcing
from .test_boundary_conditions_map import (
    plot_boundary_conditions_map,
    test_boundary_conditions_map,
)
from .test_linear_gradient import test_linear_gradient
from .test_linear_divergence import test_linear_divergence
from .test_discrete_conservation import test_discrete_conservation
from .test_swe_gradients_implementation import test_surface_gradient
from .test_swe_divergence_implementation import test_surface_divergence

__all__ = [
    "test_velocity_boundary_conditions",
    "test_tidal_forcing",
    "plot_boundary_conditions_map",
    "test_boundary_conditions_map",
    "test_linear_gradient",
    "test_linear_divergence",
    "test_discrete_conservation",
    "test_surface_gradient",
    "test_surface_divergence",
]
