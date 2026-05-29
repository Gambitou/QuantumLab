import streamlit as st

from quantumlab.repositories import (
    create_formula,
    delete_formula,
    list_formulas,
    list_hypotheses,
)


def _hypothesis_options() -> tuple[list[str], dict[str, int | None]]:
    hypotheses = list_hypotheses()
    labels = ["Sin hipotesis"]
    mapping: dict[str, int | None] = {"Sin hipotesis": None}

    for item in hypotheses:
        label = f'{item["title"]} #{item["id"]}'
        labels.append(label)
        mapping[label] = item["id"]

    return labels, mapping


def render_formulas() -> None:
    st.title("Formulas LaTeX")

    labels, mapping = _hypothesis_options()
    with st.form("create_formula", clear_on_submit=True):
        st.subheader("Nueva formula")
        title = st.text_input("Titulo", placeholder="Ej. Hamiltoniano efectivo")
        latex = st.text_area("LaTeX", placeholder=r"H = \sum_i \omega_i a_i^\dagger a_i", height=110)
        notes = st.text_area("Notas", height=90)
        selected_hypothesis = st.selectbox("Hipotesis asociada", labels)
        submitted = st.form_submit_button("Guardar formula", type="primary")

    if submitted:
        if title.strip() and latex.strip():
            create_formula(title, latex, notes, mapping[selected_hypothesis])
            st.success("Formula guardada.")
            st.rerun()
        else:
            st.error("Titulo y LaTeX son obligatorios.")

    if latex.strip():
        st.subheader("Vista previa")
        st.latex(latex)

    st.divider()
    st.subheader("Biblioteca")

    formulas = list_formulas()
    if not formulas:
        st.info("Aun no hay formulas guardadas.")
        return

    for item in formulas:
        with st.expander(f'{item["title"]} - {item["hypothesis_title"] or "Sin hipotesis"}'):
            st.caption(f'Actualizada: {item["updated_at"]}')
            st.latex(item["latex"])
            if item["notes"]:
                st.write(item["notes"])
            if st.button("Eliminar", key=f'delete_formula_{item["id"]}'):
                delete_formula(item["id"])
                st.warning("Formula eliminada.")
                st.rerun()
