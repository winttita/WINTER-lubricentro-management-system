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
    st.warning("No hay categorías cargadas. Primero cargá al menos una categoría desde la página de Categorías.")
if not proveedores:
    st.warning("No hay proveedores cargados. Primero cargá al menos un proveedor desde la página de Proveedores.")

if categorias and proveedores:
    with st.form("nuevo_producto"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre")
            codigo_interno = st.text_input("Código Interno")
            tipo_unidad = st.selectbox("Tipo de unidad", ["Entero", "Fraccionable"])
        with col2:
            codigo_barras = st.text_input("Código de Barras")
            categoria = st.selectbox("Categoría", list(cat_dict.keys()))
            proveedor = st.selectbox("Proveedor", list(prov_dict.keys()))
        
        descripcion = st.text_area("Descripción")
        
        col3, col4, col5 = st.columns(3)
        with col3:
            stock_minimo = st.number_input("Stock Mínimo", min_value=0.0)
        with col4:
            precio_costo = st.number_input("Precio Costo", min_value=0.0)
        with col5:
            precio_venta = st.number_input("Precio Venta", min_value=0.0)
            
        submitted = st.form_submit_button("Guardar Producto")
        if submitted and nombre:
            db.add_producto(codigo_interno, codigo_barras, nombre, descripcion, cat_dict[categoria], prov_dict[proveedor], tipo_unidad, stock_minimo, precio_costo, precio_venta)
            st.success("Producto agregado correctamente")

st.subheader("Listado de Productos")
productos = db.get_productos()
for p in productos:
    st.write(f"[{p[1]}] {p[3]} - {p[13]} (Stock: {p[8]})")
