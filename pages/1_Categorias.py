import streamlit as st
import database as db

st.set_page_config(page_title="Gestión de Categorías")

st.title("Categorías")

with st.form("nueva_categoria"):
    nombre = st.text_input("Nombre de la categoría")
    submitted = st.form_submit_button("Guardar")
    if submitted and nombre:
        if db.add_categoria(nombre):
            st.success("Categoría agregada")
        else:
            st.error("Error: La categoría ya existe")

st.subheader("Categorías existentes")
categorias = db.get_categorias()
for cat in categorias:
    st.write(f"- {cat[1]}")
