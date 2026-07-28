import sqlite3
import streamlit as st
import database as db
from style import inject_global_css

st.set_page_config(page_title="Gestión", layout="wide")
inject_global_css()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("⚙️ Gestión")

# --- CLIENTES ---
st.subheader("👥 Clientes")

mostrar_inactivos = st.checkbox("Mostrar inactivos", key="mostrar_clientes_inactivos")
clientes = db.get_clientes(incluir_inactivos=mostrar_inactivos)

with st.form("add_cli"):
    c1, c2, c3 = st.columns(3)
    with c1:
        cli_nombre = st.text_input("Nombre *")
    with c2:
        cli_tel = st.text_input("Teléfono")
    with c3:
        cli_email = st.text_input("Email (opcional)")
    if st.form_submit_button("Agregar Cliente"):
        if not cli_nombre.strip():
            st.error("❌ El nombre es obligatorio.")
        else:
            cli_tel = cli_tel if cli_tel else ""
            cli_email = cli_email if cli_email else ""
            if db.add_cliente(cli_nombre.strip(), cli_tel, cli_email):
                st.success("✅ Cliente agregado correctamente")
                st.rerun()
            else:
                conn = db.get_connection()
                ya_existe = conn.execute("SELECT id FROM clientes WHERE nombre = ?", (cli_nombre.strip(),)).fetchone()
                conn.close()
                if ya_existe:
                    st.error("❌ Cliente existente")
                else:
                    st.error("❌ Error al crear cliente")

if clientes:
    for c in clientes:
        activo = c[4] if len(c) > 4 else 1
        label = f"{c[1]} - {c[2] or 'Sin tel'} - {c[3] or 'Sin email'}"
        if not activo:
            label = f"🚫 {label} (inactivo)"
        with st.expander(label):
            nc1, nc2, nc3 = st.columns(3)
            with nc1:
                new_nom = st.text_input("Nombre", value=c[1], key=f"cn_{c[0]}")
            with nc2:
                new_tel = st.text_input("Teléfono", value=c[2] or "", key=f"ct_{c[0]}")
            with nc3:
                new_em = st.text_input("Email", value=c[3] or "", key=f"ce_{c[0]}")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("💾 Guardar", key=f"csave_{c[0]}"):
                    if db.update_cliente(c[0], new_nom, new_tel, new_em):
                        st.success("✅ Actualizado correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar")
            with col_b2:
                if activo:
                    if st.button("🗑️ Desactivar", key=f"cdel_{c[0]}"):
                        if db.desactivar_cliente(c[0]):
                            st.success("✅ Cliente desactivado correctamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al desactivar cliente")
                else:
                    if st.button("🔄 Reactivar", key=f"creact_{c[0]}"):
                        if db.reactivar_cliente(c[0]):
                            st.success("✅ Cliente reactivado correctamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al reactivar cliente")

st.divider()

# --- VEHICULOS ---
st.subheader("🚗 Vehículos")
clientes_activos = db.get_clientes(incluir_inactivos=False)
cliente_options = {c[1]: c[0] for c in clientes_activos}

with st.form("nuevo_vehiculo"):
    v1, v2, v3, v4, v5 = st.columns([2, 1, 2, 2, 1])
    with v1:
        v_cliente = st.selectbox("Cliente", options=list(cliente_options.keys()) if cliente_options else [])
    with v2:
        v_patente = st.text_input("Patente *")
    with v3:
        v_marca = st.text_input("Marca")
    with v4:
        v_modelo = st.text_input("Modelo")
    with v5:
        v_anio = st.number_input("Año", min_value=1900, max_value=2100, step=1, value=2020)
    if st.form_submit_button("Agregar Vehículo"):
        if v_patente and v_cliente:
            cliente_id = cliente_options.get(v_cliente)
            if db.add_vehiculo(cliente_id, v_patente, v_marca, v_modelo, v_anio):
                st.success("✅ Vehículo agregado correctamente")
                st.rerun()
            else:
                st.error("❌ Error: patente duplicada")
        else:
            st.error("❌ Patente y cliente son obligatorios")

vehiculos = db.get_vehiculos()
if vehiculos:
    for v in vehiculos:
        vid = v[0]
        with st.expander(f"**{v[2]}** - {v[3]} {v[4]} ({v[5]}) - Cliente: {v[6]}"):
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
                        st.success("✅ Actualizado correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error: patente duplicada")
            with c2:
                if st.button("🗑️ Eliminar", key=f"vd_{vid}", type="secondary"):
                    try:
                        conn = db.get_connection()
                        conn.execute("DELETE FROM vehiculos WHERE id=?", (vid,))
                        conn.commit()
                        st.success("✅ Vehículo eliminado correctamente")
                    except Exception as e:
                        if "FOREIGN KEY" in str(e) or "foreign key" in str(e).lower():
                            st.error("❌ No se puede eliminar: hay órdenes de servicio asociadas")
                        else:
                            st.error(f"❌ Error: {e}")
                    finally:
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
                st.success("✅ Proveedor agregado correctamente")
                st.rerun()
            else:
                st.error("❌ Error: nombre duplicado")

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
                        st.success("✅ Actualizado correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar proveedor")
            with c2:
                if st.button("🗑️ Eliminar", key=f"pdel_{p[0]}"):
                    try:
                        conn = db.get_connection()
                        conn.execute("DELETE FROM proveedores WHERE id=?", (p[0],))
                        conn.commit()
                        st.success("✅ Eliminado correctamente")
                    except sqlite3.IntegrityError:
                        st.error("❌ No se puede eliminar: hay productos asociados a este proveedor")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                    finally:
                        conn.close()
                    st.rerun()

            # Aumento % de precios
            st.markdown("---")
            st.markdown("**Aumento porcentual de precios**")
            col_pct, col_btn = st.columns([1, 1])
            with col_pct:
                pct = st.number_input(f"% aumento precio venta (todos los productos)", min_value=0.0, step=1.0, key=f"pct_{p[0]}")
            with col_btn:
                st.write("")
                if st.button("Aplicar aumento general", key=f"pup_{p[0]}"):
                    if pct > 0:
                        if db.aumentar_precios_proveedor(p[0], pct):
                            st.success(f"✅ Precios aumentados un {pct}% correctamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al aplicar el aumento")
                    else:
                        st.error("❌ El porcentaje debe ser mayor a 0")

            # Aumento parcial por categoria
            with st.expander("Aumento por categoria", expanded=False):
                cats_prov = db.get_categorias_por_proveedor(p[0])
                if not cats_prov:
                    st.info("ℹ️ No hay categorias asignadas a los productos de este proveedor.")
                else:
                    cat_opts = {f"{c[1]} (ID {c[0]})": c[0] for c in cats_prov}
                    sel_cat = st.selectbox(
                        "Categoria a actualizar",
                        list(cat_opts.keys()),
                        key=f"sel_cat_{p[0]}"
                    )
                    pct_cat = st.number_input(
                        "% aumento para esta categoria",
                        min_value=0.0,
                        step=1.0,
                        key=f"pct_cat_{p[0]}"
                    )
                    if st.button("Aplicar aumento a categoria", key=f"pup_cat_{p[0]}"):
                        if pct_cat <= 0:
                            st.error("❌ El porcentaje debe ser mayor a 0")
                        else:
                            cat_id = cat_opts[sel_cat]
                            actualizados = db.aumentar_precios_por_categoria(p[0], pct_cat, cat_id)
                            if actualizados > 0:
                                st.success(f"✅ {actualizados} productos actualizados un {pct_cat}% correctamente")
                                st.rerun()
                            else:
                                st.warning("⚠️ No se actualizo ningun producto (verifique categoria/proveedor)")

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
                st.success("✅ Servicio agregado correctamente")
                st.rerun()
            else:
                st.error("❌ Error al agregar servicio")

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
                    st.success("✅ Actualizado correctamente")
                    st.rerun()
                else:
                    st.error("❌ Error al actualizar servicio")
            if st.button("🗑️ Eliminar", key=f"sdel_{s[0]}"):
                try:
                    conn = db.get_connection()
                    conn.execute("DELETE FROM servicios WHERE id=?", (s[0],))
                    conn.commit()
                    st.success("✅ Servicio eliminado correctamente")
                except sqlite3.IntegrityError:
                    st.error("❌ No se puede eliminar: hay órdenes usando este servicio")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    conn.close()
                st.rerun()

st.divider()

# --- CONFIGURACION DE IMPRESORA TERMICA ---
st.subheader("🖨️ Impresora Térmica")

import tickets as tk

impresoras = tk.obtener_impresoras_disponibles()
if impresoras:
    if 'impresora_seleccionada' not in st.session_state:
        st.session_state.impresora_seleccionada = impresoras[0] if impresoras else None

    idx = 0
    if st.session_state.impresora_seleccionada in impresoras:
        idx = impresoras.index(st.session_state.impresora_seleccionada)

    sel = st.selectbox("Impresora", impresoras, index=idx)
    st.session_state.impresora_seleccionada = sel
    tk.PRINTER_NAME = sel

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🖨️ Imprimir prueba"):
            if tk.imprimir_prueba():
                st.success("✅ Impresión de prueba enviada")
            else:
                st.error("❌ Error al imprimir. Verificá que la impresora esté conectada.")

    with c2:
        if st.button("💰 Abrir cajón de dinero"):
            if tk.abrir_cajon():
                st.success("✅ Comando de apertura enviado")
            else:
                st.error("❌ Error al abrir cajón")

    st.caption(f"Impresora activa: **{sel}**")
else:
    st.warning("⚠️ No se detectaron impresoras. Conectá la impresora e instalá el driver.")
    st.caption("Driver incluido en la carpeta `drivers/` de la instalación.")
