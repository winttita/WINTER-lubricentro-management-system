import streamlit as st
import database as db

st.set_page_config(page_title="Gestión de Servicios")

st.title("Servicios")

with st.form("nuevo_servicio"):
    nombre = st.text_input("Nombre del servicio")
    precio = st.number_input("Precio", min_value=0.0, step=0.01, format="%.2f")
    submitted = st.form_submit_button("Guardar")
    if submitted and nombre:
        if db.add_servicio(nombre, precio):
            st.success("Servicio agregado")
        else:
            st.error("Error al agregar servicio (verifique nombre y precio)")

st.subheader("Servicios existentes")
servicios = db.get_servicios()
for s in servicios:
    # s: (id, nombre, precio)
    st.write(f"**{s[1]}** - ${s[2]:.2f}")