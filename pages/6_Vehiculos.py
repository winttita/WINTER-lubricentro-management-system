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
                st.rerun()
            else:
                st.error("Error al agregar vehículo (posible patente duplicada)")

st.divider()

# --- LISTADO CON EDICIÓN ---
st.subheader("Vehículos existentes")
vehiculos = db.get_vehiculos()

for v in vehiculos:
    # v: (id, cliente_id, patente, marca, modelo, anio, cliente_nombre)
    vid = v[0]
    with st.expander(f"**{v[2]}** - {v[3]} {v[4]} ({v[5]}) - Cliente: {v[6]}"):
        # Buscar el índice del cliente actual
        cliente_actual_idx = 0
        if v[1]:
            try:
                cliente_actual_idx = list(cliente_options.values()).index(v[1])
            except ValueError:
                pass
        
        new_cliente = st.selectbox("Cliente", list(cliente_options.keys()), index=cliente_actual_idx, key=f"vc_{vid}")
        new_patente = st.text_input("Patente", value=v[2], key=f"vp_{vid}")
        new_marca = st.text_input("Marca", value=v[3], key=f"vm_{vid}")
        new_modelo = st.text_input("Modelo", value=v[4], key=f"vmo_{vid}")
        new_anio = st.number_input("Año", min_value=1900, max_value=2100, value=int(v[5]) if v[5] else 2020, key=f"va_{vid}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Guardar", key=f"vs_{vid}"):
                if db.update_vehiculo(vid, cliente_options[new_cliente], new_patente, new_marca, new_modelo, new_anio):
                    st.success("Actualizado")
                    st.rerun()
                else:
                    st.error("Error (¿patente duplicada?)")
        with c2:
            if st.button("🗑️ Eliminar", key=f"vd_{vid}", type="secondary"):
                conn = db.get_connection()
                conn.execute("DELETE FROM vehiculos WHERE id=?", (vid,))
                conn.commit()
                conn.close()
                st.success("Eliminado")
                st.rerun()