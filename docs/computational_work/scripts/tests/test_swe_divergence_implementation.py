"""Validação de consistência geométrica, exatidão e conservação discreta da divergência de fluxos.

Testa:
1. Dimensões no centro das células: (Ny, Nx);
2. Exatidão para fluxos lineares: qx = a*x, qy = b*y => div = a + b (erro de máquina);
3. Conservação discreta via balanço telescópico exato: integral da divergência no volume
   igual ao fluxo líquido integrado nas fronteiras do domínio.
"""

import sys
import numpy as np


def flux_divergence_reference(grid, qx, qy):
  """Implementação de referência da divergência de fluxos centrada."""
  dx = grid["dx"]
  dy = grid["dy"]

  div_x = (qx[:, 1:] - qx[:, :-1]) / dx
  div_y = (qy[1:, :] - qy[:-1, :]) / dy

  return div_x + div_y


def test_single_grid_divergence(
    grid, qx=None, qy=None, a=2.0, b=3.0, divergence_fn=None
):
  """Valida a divergência discreta em uma única malha."""
  if divergence_fn is None:
    # 1. Tenta obter flux_divergence do escopo global do chamador (__main__, e.g., notebook)
    divergence_fn = getattr(sys.modules.get("__main__"), "flux_divergence", None)
    # 2. Se não encontrar, utiliza a implementação de referência
    if divergence_fn is None:
      divergence_fn = flux_divergence_reference

  Ny, Nx = grid["Ny"], grid["Nx"]
  dx, dy = grid["dx"], grid["dy"]

  # Se qx e qy não forem fornecidos, constrói campos lineares nas faces:
  # qx(x, y) = a * x  e  qy(x, y) = b * y  =>  div(q) = a + b (constante)
  if qx is None or qy is None:
    qx = a * grid["Xu"]
    qy = b * grid["Yv"]
    expected = np.full((Ny, Nx), a + b, dtype=np.float64)
  else:
    expected = None

  div = divergence_fn(grid, qx, qy)

  # 1. Dimensão esperada: Dq in R^{Ny x Nx}
  assert div.shape == (Ny, Nx), (
      f"Dimensão inválida para divergência: esperado {(Ny, Nx)}, obtido {div.shape}"
  )
  assert np.all(np.isfinite(div)), "A divergência contém valores NaN ou Inf."

  # 2. Exatidão numérica quando usamos o campo linear
  max_err_lin = 0.0
  if expected is not None:
    max_err_lin = np.max(np.abs(div - expected))
    assert np.allclose(div, expected, rtol=1e-12, atol=1e-12), (
        f"Falha no teste de divergência linear. Erro máximo: {max_err_lin:.2e}"
    )

  # 3. Conservação discreta por cancelamento telescópico nas faces internas:
  # sum_{j, i} div[j, i] * dx * dy == sum_j (qx[j, -1] - qx[j, 0]) * dy + sum_i (qy[-1, i] - qy[0, i]) * dx
  volume_integral = np.sum(div) * dx * dy
  boundary_flux = (
      dy * np.sum(qx[:, -1] - qx[:, 0]) + dx * np.sum(qy[-1, :] - qy[0, :])
  )
  conservation_err = abs(volume_integral - boundary_flux)

  assert np.isclose(volume_integral, boundary_flux, rtol=1e-12, atol=1e-12), (
      f"Falha na conservação discreta: integral={volume_integral}, "
      f"fronteira={boundary_flux}, erro={conservation_err:.2e}"
  )

  print(
      f"OK | div shape={div.shape} | max_err={max_err_lin:.2e} | "
      f"cons_err={conservation_err:.2e}"
  )
  return div


def test_surface_divergence(*grids, **kwargs):
  """Valida o operador de divergência nas malhas fornecidas.

  Suporta múltiplos formatos de chamada:
  - test_surface_divergence(grid_coarse, grid_fine)
  - test_surface_divergence(grid_coarse, grid_fine, a=2.0, b=3.0)
  - test_surface_divergence(grid_fine, qx=qx, qy=qy)
  - test_surface_divergence(flux_divergence, grid_coarse, grid_fine)

  Parâmetros
  ----------
  *grids : dict ou callable
      Malhas ('Nx', 'Ny', 'dx', 'dy', 'Xu', 'Yv') e/ou função de divergência.
  **kwargs :
      qx, qy : np.ndarray, opcional
          Fluxos customizados nas faces verticais e horizontais.
      a, b : float, default=(2.0, 3.0)
          Coeficientes para os fluxos lineares de teste.
      divergence_fn : callable, opcional
          Função de divergência a ser testada.
  """
  a = kwargs.get("a", 2.0)
  b = kwargs.get("b", 3.0)
  qx = kwargs.get("qx", None)
  qy = kwargs.get("qy", None)

  div_fn = kwargs.get("divergence_fn", kwargs.get("flux_divergence", None))

  grid_list = []
  for arg in grids:
    if callable(arg) and div_fn is None:
      div_fn = arg
    elif isinstance(arg, dict) and "Nx" in arg and "Ny" in arg:
      if not any(arg is g for g in grid_list):
        grid_list.append(arg)

  if div_fn is None:
    div_fn = getattr(sys.modules.get("__main__"), "flux_divergence", None)
    if div_fn is None:
      div_fn = flux_divergence_reference

  if not grid_list:
    raise ValueError(
        "Nenhuma malha válida foi fornecida para test_surface_divergence."
    )

  for i, g in enumerate(grid_list):
    nx = g.get("Nx")
    label = "Grossa" if nx == 40 else ("Fina" if nx == 120 else f"Malha {i+1}")
    print(f"[{label}]", end=" ")
    test_single_grid_divergence(
        g, qx=qx, qy=qy, a=a, b=b, divergence_fn=div_fn
    )


if __name__ == "__main__":
  # Execução direta para autoverificação autônoma no terminal
  print("Executando teste autônomo de test_swe_divergence_implementation:")
  for label, (nx, ny, dx, dy) in [
      ("Grossa", (40, 20, 150.0, 150.0)),
      ("Fina", (120, 60, 50.0, 50.0)),
  ]:
    xc = (np.arange(nx) + 0.5) * dx
    yc = (np.arange(ny) + 0.5) * dy
    xf = np.arange(nx + 1) * dx
    yf = np.arange(ny + 1) * dy
    mock_g = {
        "Nx": nx,
        "Ny": ny,
        "dx": dx,
        "dy": dy,
        "Xc": np.meshgrid(xc, yc)[0],
        "Yc": np.meshgrid(xc, yc)[1],
        "Xu": np.meshgrid(xf, yc)[0],
        "Yu": np.meshgrid(xf, yc)[1],
        "Xv": np.meshgrid(xc, yf)[0],
        "Yv": np.meshgrid(xc, yf)[1],
    }
    print(f"[{label}]", end=" ")
    test_single_grid_divergence(mock_g)



def test_surface_divergence(*grids, **kwargs):
  """Valida o operador de divergência nas malhas fornecidas.

  Suporta múltiplos formatos de chamada:
  - test_surface_divergence(grid_coarse, grid_fine)
  - test_surface_divergence(grid_coarse, grid_fine, a=2.0, b=3.0)
  - test_surface_divergence(grid_fine, qx=qx, qy=qy)
  - test_surface_divergence(flux_divergence, grid_coarse, grid_fine)

  Parâmetros
  ----------
  *grids : dict ou callable
      Malhas ('Nx', 'Ny', 'dx', 'dy', 'Xu', 'Yv') e/ou função de divergência.
  **kwargs :
      qx, qy : np.ndarray, opcional
          Fluxos customizados nas faces verticais e horizontais.
      a, b : float, default=(2.0, 3.0)
          Coeficientes para os fluxos lineares de teste.
      divergence_fn : callable, opcional
          Função de divergência a ser testada.
  """
  a = kwargs.get("a", 2.0)
  b = kwargs.get("b", 3.0)
  qx = kwargs.get("qx", None)
  qy = kwargs.get("qy", None)

  div_fn = kwargs.get("divergence_fn", kwargs.get("flux_divergence", None))

  grid_list = []
  for arg in grids:
    if callable(arg) and div_fn is None:
      div_fn = arg
    elif isinstance(arg, dict) and "Nx" in arg and "Ny" in arg:
      if not any(arg is g for g in grid_list):
        grid_list.append(arg)

  if div_fn is None:
    div_fn = getattr(sys.modules.get("__main__"), "flux_divergence", None)
    if div_fn is None:
      div_fn = flux_divergence_reference

  if not grid_list:
    raise ValueError(
        "Nenhuma malha válida foi fornecida para test_surface_divergence."
    )

  for i, g in enumerate(grid_list):
    nx = g.get("Nx")
    label = "Grossa" if nx == 40 else ("Fina" if nx == 120 else f"Malha {i+1}")
    print(f"[{label}]", end=" ")
    test_single_grid_divergence(
        g, qx=qx, qy=qy, a=a, b=b, divergence_fn=div_fn
    )


if __name__ == "__main__":
  # Execução direta para autoverificação autônoma no terminal
  print("Executando teste autônomo de test_swe_divergence_implementation:")
  for label, (nx, ny, dx, dy) in [
      ("Grossa", (40, 20, 150.0, 150.0)),
      ("Fina", (120, 60, 50.0, 50.0)),
  ]:
    xc = (np.arange(nx) + 0.5) * dx
    yc = (np.arange(ny) + 0.5) * dy
    xf = np.arange(nx + 1) * dx
    yf = np.arange(ny + 1) * dy
    mock_g = {
        "Nx": nx,
        "Ny": ny,
        "dx": dx,
        "dy": dy,
        "Xc": np.meshgrid(xc, yc)[0],
        "Yc": np.meshgrid(xc, yc)[1],
        "Xu": np.meshgrid(xf, yc)[0],
        "Yu": np.meshgrid(xf, yc)[1],
        "Xv": np.meshgrid(xc, yf)[0],
        "Yv": np.meshgrid(xc, yf)[1],
    }
    print(f"[{label}]", end=" ")
    test_single_grid_divergence(mock_g)