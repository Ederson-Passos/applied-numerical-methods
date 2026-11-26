"""Testes de consistência geométrica e exatidão para o gradiente de superfície livre.

Valida as dimensões nas faces internas e a convergência exata (erro de máquina)
para campos lineares de elevação eta(x, y) = a*x + b*y + c, além de anulação
identicamente nula para campos constantes.
"""

import sys
import numpy as np


def surface_gradient_reference(grid, eta=None):
  """Implementação de referência do gradiente discreto nas faces internas."""
  if eta is None:
    eta = grid["eta"]

  dx = grid["dx"]
  dy = grid["dy"]

  # Gradiente nas faces verticais internas: (Ny, Nx - 1)
  grad_x = (eta[:, 1:] - eta[:, :-1]) / dx

  # Gradiente nas faces horizontais internas: (Ny - 1, Nx)
  grad_y = (eta[1:, :] - eta[:-1, :]) / dy

  return grad_x, grad_y


def test_single_grid_surface_gradient(
    grid, surface_gradient_fn=None, a=2.5e-3, b=-1.2e-3, c=0.4
):
  """Valida o operador de gradiente de superfície em uma única malha."""
  if surface_gradient_fn is None:
    # 1. Tenta obter surface_gradient do escopo global do chamador (__main__, e.g., notebook)
    surface_gradient_fn = getattr(
        sys.modules.get("__main__"), "surface_gradient", None
    )
    # 2. Se não encontrar, utiliza a implementação de referência
    if surface_gradient_fn is None:
      surface_gradient_fn = surface_gradient_reference

  Ny, Nx = grid["eta"].shape
  dx, dy = grid["dx"], grid["dy"]

  # Campo linear nos centros das células: eta(x, y) = a*x + b*y + c
  eta_lin = a * grid["Xc"] + b * grid["Yc"] + c

  gx, gy = surface_gradient_fn(grid, eta=eta_lin)

  # 1. Conferência de dimensões das faces internas
  assert gx.shape == (Ny, Nx - 1), f"Esperado {(Ny, Nx - 1)}, obtido {gx.shape}"
  assert gy.shape == (Ny - 1, Nx), f"Esperado {(Ny - 1, Nx)}, obtido {gy.shape}"

  # 2. Conferência contra derivadas exatas: d(eta)/dx = a, d(eta)/dy = b
  err_x = np.max(np.abs(gx - a))
  err_y = np.max(np.abs(gy - b))

  assert np.allclose(gx, a, rtol=1e-12, atol=1e-12), f"Falha em grad_x: {err_x}"
  assert np.allclose(gy, b, rtol=1e-12, atol=1e-12), f"Falha em grad_y: {err_y}"

  # 3. Teste com campo constante (gradiente deve ser identicamente zero)
  eta_const = np.full_like(grid["eta"], 1.75, dtype=np.float64)
  gx_c, gy_c = surface_gradient_fn(grid, eta=eta_const)
  assert np.all(gx_c == 0.0) and np.all(gy_c == 0.0)

  print(
      f"OK | gx shape={gx.shape}, max_err={err_x:.2e} | "
      f"gy shape={gy.shape}, max_err={err_y:.2e}"
  )
  return True


def test_surface_gradient(*grids, **kwargs):
  """Valida o gradiente de superfície livre nas malhas fornecidas.

  Suporta múltiplos formatos de chamada:
  - test_surface_gradient(grid_coarse, grid_fine, a=..., b=..., c=...)
  - test_surface_gradient(grid, grid_coarse, grid_fine, a=..., b=..., c=...)
  - test_surface_gradient(surface_gradient, grid_coarse, grid_fine)
  - test_surface_gradient(grid_coarse)

  Parâmetros
  ----------
  *grids : dict ou callable
      Malhas (dicionários com 'Nx', 'Ny', 'dx', 'dy', 'Xc', 'Yc', 'eta') e/ou
      função de gradiente.
  **kwargs :
      a : float, default=2.5e-3
          Inclinação na direção x.
      b : float, default=-1.2e-3
          Inclinação na direção y.
      c : float, default=0.4
          Termo constante.
      surface_gradient_fn : callable, opcional
          Função personalizada para cálculo do gradiente.
  """
  a = kwargs.get("a", 2.5e-3)
  b = kwargs.get("b", -1.2e-3)
  c = kwargs.get("c", 0.4)

  grad_fn = kwargs.get(
      "surface_gradient_fn", kwargs.get("surface_gradient", None)
  )

  grid_list = []
  for arg in grids:
    if callable(arg) and grad_fn is None:
      grad_fn = arg
    elif isinstance(arg, dict) and "eta" in arg:
      # Evita malhas duplicadas caso passe (grid, grid_coarse, grid_fine)
      if not any(arg is g for g in grid_list):
        grid_list.append(arg)

  if grad_fn is None:
    grad_fn = getattr(sys.modules.get("__main__"), "surface_gradient", None)
    if grad_fn is None:
      grad_fn = surface_gradient_reference

  if not grid_list:
    raise ValueError(
        "Nenhuma malha válida foi fornecida para test_surface_gradient."
    )

  for i, g in enumerate(grid_list):
    nx = g.get("Nx")
    label = "Grossa" if nx == 40 else ("Fina" if nx == 120 else f"Malha {i+1}")
    print(f"[{label}]", end=" ")
    test_single_grid_surface_gradient(
        g, surface_gradient_fn=grad_fn, a=a, b=b, c=c
    )
