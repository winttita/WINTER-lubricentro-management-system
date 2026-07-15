import streamlit as st
import database as db

st.set_page_config(page_title="Gestión de Clientes")

st.title("Clientes")

with st.form("nuevo_cliente"):
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Teléfono")
    email = st.text_input("Email")
    submitted = st.form_submit_button("Guardar")
    if submitted and nombre:
        if db.add_cliente(nombre, telefono, email):
            st.success("Cliente agregado")
        else:
            st.error("Error al agregar cliente (verifique que el nombre no esté vacío)")

st.subheader("Clientes existentes")
clientes = db.get_clientes()
for cli in clientes:
    # cli: (id, nombre, telefono, email)
    st.write(f"**{cli[1]}** - Tel: {cli[2]} - Email: {cli[3]}")