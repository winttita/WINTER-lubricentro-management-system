import streamlit as st
import database as db

st.set_page_config(page_title="Gestión de Productos")

st.title("Productos")

# Datos necesarios para el formulario
categorias = db.get_categorias()
proveedores = db.get_proveedores()

cat_dict = {c[1]: c[0] for c in categorias}
prov_dict = {p[1]: p[0] for p in proveedores}

if not categorias:
    st.warning("No hay categorías cargadas. Primero cargá al menos una categoría desde Configuración.")
if not proveedores:
    st.warning("No hay proveedores cargados. Primero cargá al menos un proveedor desde Configuración.")

if categorias and proveedores:
     # Initialize clear flag if not present
     if 'clear_scanner' not in st.session_state:
         st.session_state.clear_scanner = False
     
     # --- ESCANER CÓDIGO DE BARRAS (fuera del form para evitar submit prematuro) ---
     # Check if we need to clear the scanner
     scanner_value = "" if st.session_state.clear_scanner else st.session_state.get("codigo_barras_scanner", "")
     st.text_input("Código de Barras (escanear)", key="codigo_barras_scanner", 
                   value=scanner_value, placeholder="Escaneá el código de barras aquí")
     # Reset the clear flag after using it
     if st.session_state.clear_scanner:
         st.session_state.clear_scanner = False
     codigo_barras = st.session_state.get("codigo_barras_scanner", "")

     # --- FORMULARIO NUEVO PRODUCTO ---
     with st.form("nuevo_producto"):
         col1, col2 = st.columns(2)
         with col1:
             nombre = st.text_input("Nombre")
             codigo_interno = st.text_input("Código Interno")
             tipo_unidad = st.selectbox("Tipo de unidad", ["Entero", "Fraccionable"])
         with col2:
             st.text_input("Código de Barras", value=codigo_barras, disabled=True)
             categoria = st.selectbox("Categoría", list(cat_dict.keys()))
             proveedor = st.selectbox("Proveedor", list(prov_dict.keys()))
         
         descripcion = st.text_area("Descripción")
         
         col3, col4, col5, col6 = st.columns(4)
         with col3:
             stock_minimo = st.number_input("Stock Mínimo", min_value=0.0)
         with col4:
             precio_costo = st.number_input("Precio Costo", min_value=0.0)
         with col5:
             precio_venta = st.number_input("Precio Venta", min_value=0.0)
         with col6:
             stock_inicial = st.number_input("Stock Inicial", min_value=0.0, value=0.0)
             
         submitted = st.form_submit_button("Guardar Producto")
         if submitted and nombre:
             db.add_producto(codigo_interno, codigo_barras, nombre, descripcion, cat_dict[categoria], prov_dict[proveedor], tipo_unidad, stock_minimo, precio_costo, precio_venta, stock_inicial=stock_inicial)
             # Set flag to clear scanner on next render
             st.session_state.clear_scanner = True
             st.success("Producto agregado correctamente")
             st.rerun()

st.divider()

# --- LISTADO CON EDICIÓN ---
st.subheader("Listado de Productos")
productos = db.get_productos()

for p in productos:
    # p: id, cod_int, cod_bar, nombre, desc, cat_id, prov_id, tipo_uni, stock, stock_min, prec_costo, prec_venta, activo, cat_nom, prov_nom
    pid = p[0]
    with st.expander(f"[{p[1]}] {p[3]} - {p[13] or 'Sin cat'} - Stock: {p[8]} - ${p[11]:.2f}"):
        col1, col2 = st.columns(2)
        with col1:
            new_nombre = st.text_input("Nombre", value=p[3], key=f"nom_{pid}")
            new_cod_int = st.text_input("Código Interno", value=p[1] or "", key=f"ci_{pid}")
            new_cod_bar = st.text_input("Código Barras", value=p[2] or "", key=f"cb_{pid}")
            new_tipo = st.selectbox("Tipo Unidad", ["Entero", "Fraccionable"], index=["Entero", "Fraccionable"].index(p[7]), key=f"tu_{pid}")
            new_cat = st.selectbox("Categoría", list(cat_dict.keys()), index=list(cat_dict.values()).index(p[5]) if p[5] in cat_dict.values() else 0, key=f"cat_{pid}")
        with col2:
            new_desc = st.text_area("Descripción", value=p[4] or "", key=f"desc_{pid}")
            new_prov = st.selectbox("Proveedor", list(prov_dict.keys()), index=list(prov_dict.values()).index(p[6]) if p[6] in prov_dict.values() else 0, key=f"prov_{pid}")
            new_stock_min = st.number_input("Stock Mínimo", value=float(p[9]), min_value=0.0, key=f"sm_{pid}")
            new_prec_costo = st.number_input("Precio Costo", value=float(p[10]), min_value=0.0, key=f"pc_{pid}")
            new_prec_venta = st.number_input("Precio Venta", value=float(p[11]), min_value=0.0, key=f"pv_{pid}")
        
        if st.button("💾 Guardar cambios", key=f"save_{pid}"):
            ok = db.update_producto(pid, new_cod_int, new_cod_bar, new_nombre, new_desc, cat_dict[new_cat], prov_dict[new_prov], new_tipo, new_stock_min, new_prec_costo, new_prec_venta)
            if ok:
                st.success("Actualizado")
                st.rerun()
            else:
                st.error("Error al actualizar (¿código duplicado?)")
        
        if st.button("🗑️ Desactivar", key=f"del_{pid}", type="secondary"):
            conn = db.get_connection()
            conn.execute("UPDATE productos SET activo=0 WHERE id=?", (pid,))
            conn.commit()
            conn.close()
            st.success("Producto desactivado")
            st.rerun()