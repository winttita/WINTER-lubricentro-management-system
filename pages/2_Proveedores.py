import streamlit as st
import database as db

st.set_page_config(page_title="Gestión de Proveedores")

st.title("Proveedores")

condiciones = [
    'Contado', 
    'Cuenta Corriente (7 días)', 
    'Cuenta Corriente (15 días)', 
    'Cuenta Corriente (30 días)', 
    'Otro'
]

with st.form("nuevo_proveedor"):
    nombre = st.text_input("Nombre")
    contacto = st.text_input("Contacto")
    telefono = st.text_input("Teléfono")
    condicion = st.selectbox("Condición de pago", condiciones)
    
    submitted = st.form_submit_button("Guardar")
    if submitted and nombre:
        db.add_proveedor(nombre, contacto, telefono, condicion)
        st.success("Proveedor agregado")

st.subheader("Proveedores existentes")
proveedores = db.get_proveedores()
for prov in proveedores:
    st.write(f"**{prov[1]}** - {prov[2]} ({prov[3]}) - Condición: {prov[4]}")
