import streamlit as st
import sqlite3
import database as db
from style import inject_global_css, mostrar_flash, flash_exito, flash_error

st.set_page_config(page_title="Gestión de Productos")
inject_global_css()
mostrar_flash()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("Productos")

# Datos necesarios para el formulario
categorias = db.get_categorias()
proveedores = db.get_proveedores()

cat_dict = {c[1]: c[0] for c in categorias}
prov_dict = {p[1]: p[0] for p in proveedores}

if not categorias:
    st.warning("⚠️ No hay categorías cargadas. Agregá una en la sección Categorías de esta página.")
if not proveedores:
    st.warning("⚠️ No hay proveedores cargados. Primero cargá al menos un proveedor desde la pestaña Gestión.")

# --- CATEGORIAS ---
st.subheader("📂 Categorías")
cat_cols = st.columns([3, 1])
with cat_cols[0]:
    with st.form("add_cat"):
        cat_nombre = st.text_input("Nueva categoría")
        if st.form_submit_button("Agregar"):
            if cat_nombre.strip():
                if db.add_categoria(cat_nombre):
                    flash_exito("Categoría agregada correctamente")
                    st.rerun()
                else:
                    flash_error("Ya existe")

if categorias:
    for c in categorias:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.write(f"• {c[1]}")
        with c2:
            if st.button("🗑️ Eliminar", key=f"del_cat_{c[0]}"):
                try:
                    conn = db.get_connection()
                    conn.execute("DELETE FROM categorias WHERE id=?", (c[0],))
                    conn.commit()
                    flash_exito("Categoría eliminada correctamente")
                except sqlite3.IntegrityError:
                    flash_error("No se puede eliminar: hay productos usando esta categoría")
                except Exception as e:
                    flash_error(f"Error: {e}")
                finally:
                    conn.close()
                st.rerun()

st.divider()

if categorias and proveedores:
     # Initialize clear flag if not present
     if 'clear_scanner' not in st.session_state:
         st.session_state.clear_scanner = False
     
     # --- ESCANER CÓDIGO DE BARRAS (fuera del form para evitar submit prematuro) ---
     # Check if we need to clear the scanner
     scanner_value = "" if st.session_state.clear_scanner else st.session_state.get("codigo_barras_scanner", "")
     if st.session_state.get("gen_codigo_f", False):
         st.session_state["codigo_barras_scanner"] = db.proximo_codigo_fraccionado()
         st.session_state["gen_codigo_f"] = False
     st.text_input("Código de Barras (escanear)", key="codigo_barras_scanner", 
                   value=scanner_value, placeholder="Escaneá el código de barras aquí")
     if st.button("Generar codigo F (sin barras)", key="gen_codigo_f"):
         st.session_state["gen_codigo_f"] = True
         st.rerun()
     # Reset the clear flag after using it
     if st.session_state.clear_scanner:
         st.session_state.clear_scanner = False
     codigo_barras = st.session_state.get("codigo_barras_scanner", "")

     # --- FORMULARIO NUEVO PRODUCTO ---
     with st.form("nuevo_producto"):
         col1, col2 = st.columns(2)
         with col1:
              nombre = st.text_input("Nombre")
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
         if submitted:
             if not nombre.strip():
                 flash_error("El nombre es obligatorio.")
             else:
                 try:
                     db.add_producto(codigo_barras, nombre, descripcion, cat_dict[categoria], prov_dict[proveedor], tipo_unidad, stock_minimo, precio_costo, precio_venta, stock_inicial=stock_inicial)
                     st.session_state.clear_scanner = True
                     flash_exito("Producto agregado correctamente")
                     st.rerun()
                 except sqlite3.IntegrityError:
                     flash_error("Error: código de barras duplicado.")

st.divider()

# --- LISTADO CON EDICIÓN ---
st.subheader("Listado de Productos")
productos = db.get_productos()

for p in productos:
    # p: id, cod_bar, nombre, desc, cat_id, prov_id, tipo_uni, stock, stock_min, prec_costo, prec_venta, activo, cat_nom, prov_nom
    pid = p[0]
    with st.expander(f"{p[2]} - {p[12] or 'Sin cat'} - Stock: {p[7]} - ${p[10]:.2f}"):
        col1, col2 = st.columns(2)
        with col1:
            new_nombre = st.text_input("Nombre", value=p[2], key=f"nom_{pid}")
            new_cod_bar = st.text_input("Código Barras", value=p[1] or "", key=f"cb_{pid}")
            if st.button("Generar F", key=f"gen_f_{pid}"):
                st.session_state[f"cb_{pid}"] = db.proximo_codigo_fraccionado()
                st.rerun()
            new_tipo = st.selectbox("Tipo Unidad", ["Entero", "Fraccionable"], index=["Entero", "Fraccionable"].index(p[6]), key=f"tu_{pid}")
            new_cat = st.selectbox("Categoría", list(cat_dict.keys()), index=list(cat_dict.values()).index(p[4]) if p[4] in cat_dict.values() else 0, key=f"cat_{pid}")
        with col2:
            new_desc = st.text_area("Descripción", value=p[3] or "", key=f"desc_{pid}")
            new_prov = st.selectbox("Proveedor", list(prov_dict.keys()), index=list(prov_dict.values()).index(p[5]) if p[5] in prov_dict.values() else 0, key=f"prov_{pid}")
            new_stock_min = st.number_input("Stock Mínimo", value=float(p[8]), min_value=0.0, key=f"sm_{pid}")
            new_prec_costo = st.number_input("Precio Costo", value=float(p[9]), min_value=0.0, key=f"pc_{pid}")
            new_prec_venta = st.number_input("Precio Venta", value=float(p[10]), min_value=0.0, key=f"pv_{pid}")
        
        if st.button("💾 Guardar cambios", key=f"save_{pid}"):
            ok = db.update_producto(pid, new_cod_bar, new_nombre, new_desc, cat_dict[new_cat], prov_dict[new_prov], new_tipo, new_stock_min, new_prec_costo, new_prec_venta)
            if ok:
                flash_exito("Actualizado correctamente")
                st.rerun()
            else:
                flash_error("Error al actualizar (¿código duplicado?)")
        
        if st.button("🗑️ Desactivar", key=f"del_{pid}", type="secondary"):
            conn = db.get_connection()
            cur = conn.execute("UPDATE productos SET activo=0 WHERE id=?", (pid,))
            conn.commit()
            conn.close()
            if cur.rowcount == 1:
                flash_exito("Producto desactivado correctamente")
                st.rerun()
            else:
                flash_error("No se pudo desactivar el producto.")