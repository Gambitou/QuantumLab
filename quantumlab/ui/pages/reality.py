from __future__ import annotations

import json

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from quantumlab.reality_engine import (
    plotly_colorscale,
    simulate_dynamic_system,
    simulate_information_field,
    simulate_particles,
    simulate_sandbox,
)
from quantumlab.repositories import (
    delete_reality_simulation,
    list_reality_simulations,
    save_reality_simulation,
)


def _particle_figure(frames: np.ndarray, frame_index: int, animated: bool) -> go.Figure:
    current = frames[frame_index]
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=current[:, 0],
            y=current[:, 1],
            mode="markers",
            marker={"size": 9, "color": "#22d3ee", "line": {"width": 1, "color": "#e5eefc"}},
            name="particulas",
        )
    )
    if animated:
        step = max(1, len(frames) // 70)
        figure.frames = [
            go.Frame(
                data=[
                    go.Scatter(
                        x=frames[index, :, 0],
                        y=frames[index, :, 1],
                        mode="markers",
                        marker={"size": 9, "color": "#22d3ee", "line": {"width": 1, "color": "#e5eefc"}},
                    )
                ],
                name=str(index),
            )
            for index in range(0, len(frames), step)
        ]
        figure.update_layout(
            updatemenus=[
                {
                    "type": "buttons",
                    "buttons": [
                        {
                            "label": "Play",
                            "method": "animate",
                            "args": [None, {"frame": {"duration": 65, "redraw": True}}],
                        }
                    ],
                }
            ]
        )
    figure.update_layout(
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1020",
        xaxis={"range": [-2.3, 2.3], "gridcolor": "#283247", "zerolinecolor": "#64748b"},
        yaxis={"range": [-2.3, 2.3], "gridcolor": "#283247", "zerolinecolor": "#64748b", "scaleanchor": "x"},
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        font={"color": "#e5eefc"},
    )
    return figure


def _heatmap_figure(frames: np.ndarray, frame_index: int, animated: bool, zmax: float = 1.0) -> go.Figure:
    colorscale = plotly_colorscale("magma")
    figure = go.Figure(
        data=[
            go.Heatmap(
                z=frames[frame_index],
                colorscale=colorscale,
                zmin=0,
                zmax=zmax,
                showscale=False,
            )
        ]
    )
    if animated:
        step = max(1, len(frames) // 60)
        figure.frames = [
            go.Frame(
                data=[go.Heatmap(z=frames[index], colorscale=colorscale, zmin=0, zmax=zmax, showscale=False)],
                name=str(index),
            )
            for index in range(0, len(frames), step)
        ]
        figure.update_layout(
            updatemenus=[
                {
                    "type": "buttons",
                    "buttons": [
                        {
                            "label": "Play",
                            "method": "animate",
                            "args": [None, {"frame": {"duration": 80, "redraw": True}}],
                        }
                    ],
                }
            ]
        )
    figure.update_layout(
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1020",
        xaxis={"visible": False},
        yaxis={"visible": False, "scaleanchor": "x"},
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        font={"color": "#e5eefc"},
    )
    return figure


def _line_figure(series: dict[str, np.ndarray], title: str = "") -> go.Figure:
    figure = go.Figure()
    for name, values in series.items():
        figure.add_trace(go.Scatter(y=values, mode="lines", name=name))
    figure.update_layout(
        title=title,
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1020",
        xaxis={"gridcolor": "#283247"},
        yaxis={"gridcolor": "#283247"},
        margin={"l": 20, "r": 20, "t": 36, "b": 20},
        font={"color": "#e5eefc"},
    )
    return figure


def _save_panel(prefix: str, simulation_type: str, parameters: dict, summary: str) -> None:
    with st.form(f"save_{prefix}", clear_on_submit=True):
        title = st.text_input("Nombre", placeholder=f"{simulation_type} experimental")
        submitted = st.form_submit_button("Guardar simulacion", type="primary")
    if submitted:
        if not title.strip():
            st.error("El nombre es obligatorio.")
            return
        save_reality_simulation(title, simulation_type, parameters, summary)
        st.success("Simulacion guardada.")
        st.rerun()


def _render_particles() -> None:
    left, right = st.columns((0.85, 1.35))
    with left:
        particle_count = st.slider("Particulas", 8, 180, 56, 4)
        steps = st.slider("Pasos", 30, 300, 140, 10)
        dt = st.slider("Delta temporal", 0.01, 0.15, 0.05, 0.01)
        force_mode = st.selectbox("Campo fisico", ["Oscilador central", "Atraccion radial", "Regla personalizada"])
        force_strength = st.slider("Intensidad", 0.0, 4.0, 1.0, 0.1)
        damping = st.slider("Amortiguacion", 0.0, 1.2, 0.12, 0.02)
        speed_limit = st.slider("Limite de velocidad", 0.1, 4.0, 1.4, 0.1)
        quantization_step = st.slider("Celda de cuantizacion", 0.0, 0.5, 0.08, 0.01)
        seed = st.number_input("Semilla", min_value=0, value=42, step=1)
        ax_expression = "-k * x - damping * vx"
        ay_expression = "-k * y - damping * vy"
        if force_mode == "Regla personalizada":
            ax_expression = st.text_input("Aceleracion X", value=ax_expression)
            ay_expression = st.text_input("Aceleracion Y", value=ay_expression)

    try:
        result = simulate_particles(
            particle_count,
            steps,
            dt,
            force_mode,
            force_strength,
            damping,
            speed_limit,
            quantization_step,
            int(seed),
            ax_expression,
            ay_expression,
        )
    except ValueError as error:
        st.error(str(error))
        return

    with right:
        frame_index = st.slider("Instante", 0, steps - 1, steps - 1, key="particle_frame")
        animated = st.toggle("Animacion", value=True, key="particle_animation")
        st.plotly_chart(_particle_figure(result.frames, frame_index, animated), use_container_width=True)

    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Velocidad media", f'{result.metrics["mean_speed"]:.3f}')
    metric_b.metric("Niveles ocupados", result.metrics["occupied_levels"])
    metric_c.metric("Limite", f'{result.metrics["speed_limit"]:.2f}')
    st.plotly_chart(_line_figure(result.series), use_container_width=True)

    _save_panel(
        "particles",
        "Particulas",
        {
            "particle_count": particle_count,
            "steps": steps,
            "dt": dt,
            "force_mode": force_mode,
            "force_strength": force_strength,
            "damping": damping,
            "speed_limit": speed_limit,
            "quantization_step": quantization_step,
            "seed": int(seed),
            "ax_expression": ax_expression,
            "ay_expression": ay_expression,
        },
        f'{particle_count} particulas, velocidad media {result.metrics["mean_speed"]:.3f}',
    )


def _render_information() -> None:
    left, right = st.columns((0.85, 1.35))
    with left:
        grid_size = st.slider("Resolucion", 24, 96, 56, 4)
        steps = st.slider("Pasos", 20, 240, 110, 10, key="info_steps")
        transmission_radius = st.slider("Radio maximo por paso", 1, 8, 2)
        diffusion = st.slider("Difusion", 0.05, 0.9, 0.38, 0.01)
        decay = st.slider("Perdida", 0.0, 0.12, 0.02, 0.005)
        pulse_strength = st.slider("Pulso inicial", 0.1, 1.0, 1.0, 0.05)

    result = simulate_information_field(
        grid_size,
        steps,
        transmission_radius,
        diffusion,
        decay,
        pulse_strength,
    )

    with right:
        frame_index = st.slider("Instante", 0, steps - 1, steps - 1, key="info_frame")
        animated = st.toggle("Animacion", value=True, key="info_animation")
        st.plotly_chart(_heatmap_figure(result.frames, frame_index, animated), use_container_width=True)

    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Informacion total", f'{result.metrics["total_information"]:.3f}')
    metric_b.metric("Pico local", f'{result.metrics["peak"]:.3f}')
    metric_c.metric("Radio", result.metrics["transmission_radius"])
    st.plotly_chart(_line_figure(result.series), use_container_width=True)

    _save_panel(
        "information",
        "Propagacion",
        {
            "grid_size": grid_size,
            "steps": steps,
            "transmission_radius": transmission_radius,
            "diffusion": diffusion,
            "decay": decay,
            "pulse_strength": pulse_strength,
        },
        f'campo {grid_size}x{grid_size}, informacion total {result.metrics["total_information"]:.3f}',
    )


def _render_dynamics() -> None:
    left, right = st.columns((0.85, 1.35))
    with left:
        system_name = st.selectbox("Sistema", ["Lorenz", "Mapa logistico"])
        steps = st.slider("Muestras", 80, 1200, 420, 20)
        duration = st.slider("Duracion", 4.0, 60.0, 24.0, 1.0)
        initial_x = st.slider("Estado inicial X", 0.01, 2.0, 0.8, 0.01)
        sigma = st.slider("Sigma", 1.0, 20.0, 10.0, 0.5)
        rho = st.slider("Rho", 1.0, 45.0, 28.0, 0.5)
        beta = st.slider("Beta", 0.5, 6.0, 2.67, 0.01)
        growth = st.slider("Crecimiento", 2.4, 4.0, 3.72, 0.01)

    result = simulate_dynamic_system(
        system_name,
        steps,
        duration,
        sigma,
        rho,
        beta,
        growth,
        initial_x,
    )

    with right:
        if system_name == "Lorenz":
            trajectory = result.frames
            figure = go.Figure(
                data=[
                    go.Scatter3d(
                        x=trajectory[:, 0],
                        y=trajectory[:, 1],
                        z=trajectory[:, 2],
                        mode="lines",
                        line={"color": trajectory[:, 2], "colorscale": "Viridis", "width": 4},
                    )
                ]
            )
            figure.update_layout(
                height=560,
                paper_bgcolor="rgba(0,0,0,0)",
                scene={
                    "bgcolor": "#0b1020",
                    "xaxis": {"gridcolor": "#283247"},
                    "yaxis": {"gridcolor": "#283247"},
                    "zaxis": {"gridcolor": "#283247"},
                },
                margin={"l": 0, "r": 0, "t": 20, "b": 0},
                font={"color": "#e5eefc"},
            )
            st.plotly_chart(figure, use_container_width=True)
        else:
            st.plotly_chart(_line_figure({"x": result.series["x"]}, "Mapa logistico"), use_container_width=True)

    st.plotly_chart(_line_figure(result.series), use_container_width=True)
    _save_panel(
        "dynamics",
        system_name,
        {
            "system_name": system_name,
            "steps": steps,
            "duration": duration,
            "initial_x": initial_x,
            "sigma": sigma,
            "rho": rho,
            "beta": beta,
            "growth": growth,
        },
        json.dumps(result.metrics, ensure_ascii=True),
    )


def _render_sandbox() -> None:
    left, right = st.columns((0.85, 1.35))
    with left:
        grid_size = st.slider("Resolucion", 20, 120, 64, 4, key="sandbox_grid")
        steps = st.slider("Pasos", 20, 260, 130, 10, key="sandbox_steps")
        density = st.slider("Densidad inicial", 0.02, 0.8, 0.24, 0.01)
        seed = st.number_input("Semilla", min_value=0, value=7, step=1, key="sandbox_seed")
        rule_mode = st.selectbox("Modo de regla", ["B/S", "Expresion"])
        if rule_mode == "B/S":
            rule_text = st.text_input("Regla", value="B3/S23")
        else:
            rule_text = st.text_area(
                "Regla",
                value="((state == 1) & ((n == 2) | (n == 3))) | ((state == 0) & (n == 3))",
                height=110,
            )

    try:
        result = simulate_sandbox(
            grid_size,
            steps,
            density,
            int(seed),
            rule_mode,
            rule_text,
        )
    except ValueError as error:
        st.error(str(error))
        return

    with right:
        frame_index = st.slider("Instante", 0, steps - 1, steps - 1, key="sandbox_frame")
        animated = st.toggle("Animacion", value=True, key="sandbox_animation")
        st.plotly_chart(_heatmap_figure(result.frames, frame_index, animated, zmax=1.0), use_container_width=True)

    metric_a, metric_b = st.columns(2)
    metric_a.metric("Celdas activas", result.metrics["live_cells"])
    metric_b.metric("Densidad final", f'{result.metrics["density"]:.3f}')
    st.plotly_chart(_line_figure(result.series), use_container_width=True)

    _save_panel(
        "sandbox",
        "Sandbox",
        {
            "grid_size": grid_size,
            "steps": steps,
            "density": density,
            "seed": int(seed),
            "rule_mode": rule_mode,
            "rule_text": rule_text,
        },
        f'{result.metrics["live_cells"]} celdas activas finales',
    )


def _render_saved_simulations() -> None:
    st.subheader("Simulaciones guardadas")
    simulations = list_reality_simulations()
    if not simulations:
        st.info("Aun no hay simulaciones guardadas.")
        return

    for simulation in simulations:
        with st.expander(f'{simulation["title"]} - {simulation["simulation_type"]}'):
            st.caption(simulation["created_at"])
            if simulation["summary"]:
                st.write(simulation["summary"])
            st.json(simulation["parameters_data"], expanded=False)
            if st.button("Eliminar simulacion", key=f'delete_reality_{simulation["id"]}'):
                delete_reality_simulation(simulation["id"])
                st.warning("Simulacion eliminada.")
                st.rerun()


def render_reality_engine() -> None:
    st.title("Reality Engine")

    particles, information, dynamics, sandbox, saved = st.tabs(
        [
            "Particulas",
            "Propagacion",
            "Sistemas dinamicos",
            "Sandbox",
            "Guardadas",
        ]
    )
    with particles:
        _render_particles()
    with information:
        _render_information()
    with dynamics:
        _render_dynamics()
    with sandbox:
        _render_sandbox()
    with saved:
        _render_saved_simulations()
