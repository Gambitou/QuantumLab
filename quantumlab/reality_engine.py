from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any

import matplotlib as mpl
import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import convolve2d


Array = np.ndarray

SAFE_FUNCTIONS = {
    "abs": np.abs,
    "clip": np.clip,
    "cos": np.cos,
    "exp": np.exp,
    "maximum": np.maximum,
    "minimum": np.minimum,
    "sin": np.sin,
    "sqrt": np.sqrt,
    "tanh": np.tanh,
    "where": np.where,
}

SAFE_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.Call,
    ast.Load,
    ast.Name,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.USub,
    ast.UAdd,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.BitAnd,
    ast.BitOr,
    ast.BitXor,
)


@dataclass(frozen=True)
class SimulationResult:
    frames: Array
    metrics: dict[str, Any]
    series: dict[str, Array]


def plotly_colorscale(name: str = "viridis", stops: int = 8) -> list[list[Any]]:
    cmap = mpl.colormaps.get_cmap(name)
    return [
        [index / (stops - 1), mpl.colors.to_hex(cmap(index / (stops - 1)))]
        for index in range(stops)
    ]


def _safe_eval_expression(expression: str, variables: dict[str, Any]) -> Any:
    tree = ast.parse(expression, mode="eval")
    allowed_names = set(variables).union(SAFE_FUNCTIONS)

    for node in ast.walk(tree):
        if not isinstance(node, SAFE_NODES):
            raise ValueError(f"Nodo no permitido: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            raise ValueError(f"Nombre no permitido: {node.id}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in SAFE_FUNCTIONS:
                raise ValueError("Funcion no permitida")

    return eval(
        compile(tree, "<reality-rule>", "eval"),
        {"__builtins__": {}},
        {**SAFE_FUNCTIONS, **variables},
    )


def _as_vector(value: Any, shape: tuple[int, ...]) -> Array:
    array = np.asarray(value, dtype=float)
    if array.shape == ():
        return np.full(shape, float(array))
    return np.broadcast_to(array, shape)


def _limit_speed(velocities: Array, speed_limit: float) -> Array:
    speeds = np.linalg.norm(velocities, axis=1)
    mask = speeds > speed_limit
    if np.any(mask):
        velocities[mask] *= (speed_limit / speeds[mask])[:, None]
    return velocities


def simulate_particles(
    particle_count: int,
    steps: int,
    dt: float,
    force_mode: str,
    force_strength: float,
    damping: float,
    speed_limit: float,
    quantization_step: float,
    seed: int,
    ax_expression: str = "-k * x - damping * vx",
    ay_expression: str = "-k * y - damping * vy",
) -> SimulationResult:
    rng = np.random.default_rng(seed)
    positions = rng.uniform(-1.0, 1.0, size=(particle_count, 2))
    velocities = rng.normal(0.0, 0.18, size=(particle_count, 2))
    frames = np.zeros((steps, particle_count, 2), dtype=float)
    mean_speed = np.zeros(steps, dtype=float)
    occupied_levels = np.zeros(steps, dtype=float)

    for step in range(steps):
        x = positions[:, 0]
        y = positions[:, 1]
        vx = velocities[:, 0]
        vy = velocities[:, 1]

        if force_mode == "Regla personalizada":
            variables = {
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "t": step * dt,
                "k": force_strength,
                "damping": damping,
                "c": speed_limit,
            }
            acceleration = np.column_stack(
                (
                    _as_vector(_safe_eval_expression(ax_expression, variables), x.shape),
                    _as_vector(_safe_eval_expression(ay_expression, variables), y.shape),
                )
            )
        elif force_mode == "Atraccion radial":
            radius = np.linalg.norm(positions, axis=1) + 1e-6
            acceleration = -force_strength * positions / radius[:, None]
            acceleration -= damping * velocities
        else:
            acceleration = -force_strength * positions - damping * velocities

        velocities += acceleration * dt
        velocities = _limit_speed(velocities, speed_limit)
        positions += velocities * dt

        if quantization_step > 0:
            positions = np.round(positions / quantization_step) * quantization_step

        positions = np.clip(positions, -2.2, 2.2)
        frames[step] = positions
        mean_speed[step] = np.mean(np.linalg.norm(velocities, axis=1))
        occupied_levels[step] = len(np.unique(np.round(positions, 3), axis=0))

    return SimulationResult(
        frames=frames,
        metrics={
            "mean_speed": float(mean_speed[-1]),
            "occupied_levels": int(occupied_levels[-1]),
            "speed_limit": speed_limit,
        },
        series={"mean_speed": mean_speed, "occupied_levels": occupied_levels},
    )


def simulate_information_field(
    grid_size: int,
    steps: int,
    transmission_radius: int,
    diffusion: float,
    decay: float,
    pulse_strength: float,
) -> SimulationResult:
    grid = np.zeros((grid_size, grid_size), dtype=float)
    center = grid_size // 2
    frames = np.zeros((steps, grid_size, grid_size), dtype=float)
    total_information = np.zeros(steps, dtype=float)
    radius = max(1, int(transmission_radius))
    kernel = np.ones((radius * 2 + 1, radius * 2 + 1), dtype=float)
    kernel[radius, radius] = 0.0
    kernel /= np.sum(kernel)

    for step in range(steps):
        if step < max(2, steps // 8):
            grid[center, center] = pulse_strength
        neighbor_average = convolve2d(grid, kernel, mode="same", boundary="fill", fillvalue=0)
        grid = grid + diffusion * (neighbor_average - grid)
        grid *= 1.0 - decay
        grid = np.clip(grid, 0.0, 1.0)
        frames[step] = grid
        total_information[step] = np.sum(grid)

    return SimulationResult(
        frames=frames,
        metrics={
            "peak": float(np.max(frames[-1])),
            "total_information": float(total_information[-1]),
            "transmission_radius": radius,
        },
        series={"total_information": total_information},
    )


def simulate_dynamic_system(
    system_name: str,
    steps: int,
    duration: float,
    sigma: float,
    rho: float,
    beta: float,
    growth: float,
    initial_x: float,
) -> SimulationResult:
    if system_name == "Mapa logistico":
        values = np.zeros(steps, dtype=float)
        values[0] = initial_x
        for step in range(1, steps):
            values[step] = growth * values[step - 1] * (1.0 - values[step - 1])
        frames = values[:, None]
        return SimulationResult(
            frames=frames,
            metrics={"final": float(values[-1]), "maximum": float(np.max(values))},
            series={"x": values},
        )

    def lorenz(_time: float, state: list[float]) -> list[float]:
        x, y, z = state
        return [
            sigma * (y - x),
            x * (rho - z) - y,
            x * y - beta * z,
        ]

    times = np.linspace(0.0, duration, steps)
    solution = solve_ivp(
        lorenz,
        (0.0, duration),
        [initial_x, 1.0, 1.05],
        t_eval=times,
        rtol=1e-7,
        atol=1e-9,
    )
    trajectory = solution.y.T
    return SimulationResult(
        frames=trajectory,
        metrics={
            "final_x": float(trajectory[-1, 0]),
            "final_y": float(trajectory[-1, 1]),
            "final_z": float(trajectory[-1, 2]),
        },
        series={"x": trajectory[:, 0], "y": trajectory[:, 1], "z": trajectory[:, 2]},
    )


def _parse_life_rule(rule_text: str) -> tuple[set[int], set[int]]:
    match = re.fullmatch(r"\s*B([0-8]*)/S([0-8]*)\s*", rule_text.upper())
    if not match:
        raise ValueError("Usa formato B3/S23 o una expresion personalizada.")
    birth = {int(value) for value in match.group(1)}
    survival = {int(value) for value in match.group(2)}
    return birth, survival


def simulate_sandbox(
    grid_size: int,
    steps: int,
    density: float,
    seed: int,
    rule_mode: str,
    rule_text: str,
) -> SimulationResult:
    rng = np.random.default_rng(seed)
    grid = (rng.random((grid_size, grid_size)) < density).astype(int)
    frames = np.zeros((steps, grid_size, grid_size), dtype=int)
    live_cells = np.zeros(steps, dtype=float)
    kernel = np.array(
        [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ],
        dtype=int,
    )

    if rule_mode == "B/S":
        birth, survival = _parse_life_rule(rule_text)
    else:
        birth = set()
        survival = set()

    yy, xx = np.indices((grid_size, grid_size))

    for step in range(steps):
        frames[step] = grid
        live_cells[step] = np.sum(grid)
        neighbors = convolve2d(grid, kernel, mode="same", boundary="wrap")

        if rule_mode == "B/S":
            next_grid = (
                ((grid == 0) & np.isin(neighbors, list(birth)))
                | ((grid == 1) & np.isin(neighbors, list(survival)))
            )
        else:
            variables = {
                "state": grid,
                "n": neighbors,
                "t": step,
                "x": xx,
                "y": yy,
            }
            next_grid = _safe_eval_expression(rule_text, variables)

        grid = np.asarray(next_grid, dtype=bool).astype(int)

    return SimulationResult(
        frames=frames,
        metrics={
            "live_cells": int(live_cells[-1]),
            "density": float(live_cells[-1] / (grid_size * grid_size)),
        },
        series={"live_cells": live_cells},
    )
