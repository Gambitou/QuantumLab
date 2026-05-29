from html import escape

import streamlit as st

from quantumlab.repositories import (
    STATUS_OPTIONS,
    create_hypothesis,
    delete_hypothesis,
    list_hypotheses,
    update_hypothesis,
)


def _render_tags(tags: str) -> None:
    if not tags.strip():
        return

    html = "".join(
        f'<span class="ql-tag">{escape(tag.strip())}</span>'
        for tag in tags.split(",")
        if tag.strip()
    )
    st.markdown(html, unsafe_allow_html=True)


def render_hypotheses() -> None:
    st.title("Hipotesis")

    with st.form("create_hypothesis", clear_on_submit=True):
        st.subheader("Nueva hipotesis")
        title = st.text_input("Titulo", placeholder="Ej. Coherencia cuantica en redes de sensores")
        summary = st.text_area("Resumen", height=120)
        col_a, col_b = st.columns((1, 1))
        status = col_a.selectbox("Estado", STATUS_OPTIONS)
        tags = col_b.text_input("Etiquetas", placeholder="cuantica, sensores, simulacion")
        submitted = st.form_submit_button("Guardar hipotesis", type="primary")

    if submitted:
        if title.strip():
            create_hypothesis(title, summary, status, tags)
            st.success("Hipotesis guardada.")
            st.rerun()
        else:
            st.error("El titulo es obligatorio.")

    st.divider()
    st.subheader("Registro")

    hypotheses = list_hypotheses()
    if not hypotheses:
        st.info("Aun no hay hipotesis guardadas.")
        return

    for item in hypotheses:
        with st.expander(f'{item["title"]} - {item["status"]}', expanded=False):
            st.caption(f'Actualizada: {item["updated_at"]} - Formulas: {item["formula_count"]}')
            _render_tags(item["tags"])

            with st.form(f'edit_hypothesis_{item["id"]}'):
                edit_title = st.text_input("Titulo", value=item["title"], key=f'title_{item["id"]}')
                edit_summary = st.text_area(
                    "Resumen",
                    value=item["summary"],
                    height=130,
                    key=f'summary_{item["id"]}',
                )
                col_a, col_b = st.columns((1, 1))
                edit_status = col_a.selectbox(
                    "Estado",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(item["status"])
                    if item["status"] in STATUS_OPTIONS
                    else 0,
                    key=f'status_{item["id"]}',
                )
                edit_tags = col_b.text_input(
                    "Etiquetas",
                    value=item["tags"],
                    key=f'tags_{item["id"]}',
                )
                col_save, col_delete = st.columns((1, 1))
                save = col_save.form_submit_button("Actualizar")
                remove = col_delete.form_submit_button("Eliminar")

            if save:
                if edit_title.strip():
                    update_hypothesis(
                        item["id"],
                        edit_title,
                        edit_summary,
                        edit_status,
                        edit_tags,
                    )
                    st.success("Hipotesis actualizada.")
                    st.rerun()
                else:
                    st.error("El titulo es obligatorio.")

            if remove:
                delete_hypothesis(item["id"])
                st.warning("Hipotesis eliminada.")
                st.rerun()
