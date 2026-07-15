import streamlit as st
import database as db

st.set_page_config(page_title="Gestión de Vehículos")

st.title("Vehículos")

# Load clients for dropdown
clientes = db.get_clientes()
cliente_options = {c[1]: c[0] for c in clientes}  # name -> id

with st.form("nuevo_vehiculo"):
    cliente = st.selectbox("Cliente", options=list(cliente_options.keys()) if cliente_options else [])
    patente = st.text_input("Patente")
    marca = st.text_input("Marca")
    modelo = st.text_input("Modelo")
    anio = st.number_input("Año", min_value=1900, max_value=2100, step=1, value=2020)
    submitted = st.form_submit_button("Guardar")
    if submitted and patente:
        cliente_id = cliente_options.get(cliente) if cliente else None
        if cliente_id is None:
            st.error("Seleccione un cliente")
        else:
            if db.add_vehiculo(cliente_id, patente, marca, modelo, anio):
                st.success("Vehículo agregado")
            else:
                st.error("Error al agregar vehículo (posible patente duplicada)")

st.subheader("Vehículos existentes")
vehiculos = db.get_vehiculos()
for v in vehiculos:
    # v: (id, cliente_id, patente, marca, modelo, anio, cliente_nombre)
    st.write(f"**{v[2]}** - {v[3]} {v[4]} ({v[5]}) - Cliente: {v[6]}")