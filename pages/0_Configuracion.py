import streamlit as st
import database as db

st.set_page_config(page_title="Configuración", layout="wide")
st.title("⚙️ Configuración")

# --- CATORIAS ---
st.subheader("📂 Categorías")
categorias = db.get_categorias()
cat_cols = st.columns([3, 1])
with cat_cols[0]:
    with st.form("add_cat"):
        cat_nombre = st.text_input("Nueva categoría")
        if st.form_submit_button("Agregar"):
            if cat_nombre:
                if db.add_categoria(cat_nombre):
                    st.success("Categoría agregada")
                    st.rerun()
                else:
                    st.error("Ya existe")

if categorias:
    for c in categorias:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.write(f"• {c[1]}")
        with c2:
            if st.button("🗑️", key=f"del_cat_{c[0]}"):
                conn = db.get_connection()
                conn.execute("DELETE FROM categorias WHERE id=?", (c[0],))
                conn.commit()
                conn.close()
                st.rerun()

st.divider()

# --- PROVEEDORES ---
st.subheader("🚚 Proveedores")
proveedores = db.get_proveedores()
condiciones = ['Contado', 'Cuenta Corriente (7 días)', 'Cuenta Corriente (15 días)', 'Cuenta Corriente (30 días)', 'Otro']

with st.form("add_prov"):
    p1, p2, p3 = st.columns(3)
    with p1:
        prov_nombre = st.text_input("Nombre *")
    with p2:
        prov_contacto = st.text_input("Contacto")
    with p3:
        prov_telefono = st.text_input("Teléfono")
    prov_cond = st.selectbox("Condición de pago", condiciones)
    if st.form_submit_button("Agregar Proveedor"):
        if prov_nombre:
            if db.add_proveedor(prov_nombre, prov_contacto, prov_telefono, prov_cond):
                st.success("Proveedor agregado")
                st.rerun()
            else:
                st.error("Error (¿nombre duplicado?)")

if proveedores:
    for p in proveedores:
        with st.expander(f"{p[1]} - {p[4]}"):
            np1, np2, np3 = st.columns(3)
            with np1:
                new_nom = st.text_input("Nombre", value=p[1], key=f"pn_{p[0]}")
            with np2:
                new_con = st.text_input("Contacto", value=p[2] or "", key=f"pc_{p[0]}")
            with np3:
                new_tel = st.text_input("Teléfono", value=p[3] or "", key=f"pt_{p[0]}")
            new_cond = st.selectbox("Condición", condiciones, index=condiciones.index(p[4]) if p[4] in condiciones else 0, key=f"pcond_{p[0]}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Guardar", key=f"psave_{p[0]}"):
                    if db.update_proveedor(p[0], new_nom, new_con, new_tel, new_cond):
                        st.success("Actualizado")
                        st.rerun()
                    else:
                        st.error("Error")
            with c2:
                if st.button("🗑️ Eliminar", key=f"pdel_{p[0]}"):
                    conn = db.get_connection()
                    conn.execute("DELETE FROM proveedores WHERE id=?", (p[0],))
                    conn.commit()
                    conn.close()
                    st.rerun()

st.divider()

# --- CLIENTES ---
st.subheader("👥 Clientes")
clientes = db.get_clientes()

with st.form("add_cli"):
    c1, c2, c3 = st.columns(3)
    with c1:
        cli_nombre = st.text_input("Nombre *")
    with c2:
        cli_tel = st.text_input("Teléfono")
    with c3:
        cli_email = st.text_input("Email (opcional)")
    if st.form_submit_button("Agregar Cliente"):
        if cli_nombre:
            conn = db.get_connection()
            try:
                conn.execute("INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)", (cli_nombre, cli_tel, cli_email))
                conn.commit()
                st.success("Cliente agregado")
                st.rerun()
            except:
                st.error("Error")
            finally:
                conn.close()

if clientes:
    for c in clientes:
        with st.expander(f"{c[1]} - {c[2] or 'Sin tel'} - {c[3] or 'Sin email'}"):
            nc1, nc2, nc3 = st.columns(3)
            with nc1:
                new_nom = st.text_input("Nombre", value=c[1], key=f"cn_{c[0]}")
            with nc2:
                new_tel = st.text_input("Teléfono", value=c[2] or "", key=f"ct_{c[0]}")
            with nc3:
                new_em = st.text_input("Email", value=c[3] or "", key=f"ce_{c[0]}")
            if st.button("💾 Guardar", key=f"csave_{c[0]}"):
                if db.update_cliente(c[0], new_nom, new_tel, new_em):
                    st.success("Actualizado")
                    st.rerun()
                else:
                    st.error("Error")
            if st.button("🗑️ Eliminar", key=f"cdel_{c[0]}"):
                conn = db.get_connection()
                conn.execute("DELETE FROM clientes WHERE id=?", (c[0],))
                conn.commit()
                conn.close()
                st.rerun()

st.divider()

# --- SERVICIOS ---
st.subheader("🔧 Servicios")
servicios = db.get_servicios()

with st.form("add_serv"):
    s1, s2 = st.columns(2)
    with s1:
        serv_nombre = st.text_input("Nombre *")
    with s2:
        serv_precio = st.number_input("Precio *", min_value=0.0, step=0.01)
    if st.form_submit_button("Agregar Servicio"):
        if serv_nombre:
            if db.add_servicio(serv_nombre, serv_precio):
                st.success("Servicio agregado")
                st.rerun()
            else:
                st.error("Error")

if servicios:
    for s in servicios:
        with st.expander(f"{s[1]} - ${s[2]:.2f}"):
            ns1, ns2 = st.columns(2)
            with ns1:
                new_nom = st.text_input("Nombre", value=s[1], key=f"sn_{s[0]}")
            with ns2:
                new_pre = st.number_input("Precio", value=float(s[2]), min_value=0.0, key=f"sp_{s[0]}")
            if st.button("💾 Guardar", key=f"ssave_{s[0]}"):
                if db.update_servicio(s[0], new_nom, new_pre):
                    st.success("Actualizado")
                    st.rerun()
                else:
                    st.error("Error")
            if st.button("🗑️ Eliminar", key=f"sdel_{s[0]}"):
                conn = db.get_connection()
                conn.execute("DELETE FROM servicios WHERE id=?", (s[0],))
                conn.commit()
                conn.close()
                st.rerun()