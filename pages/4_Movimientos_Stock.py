import streamlit as st
import database as db
from datetime import date

st.set_page_config(page_title="Historial de Stock")
st.title("📦 Historial de Movimientos de Stock")

# Filtros
col1, col2, col3 = st.columns(3)
with col1:
    fecha_desde = st.date_input("Desde", value=None)
with col2:
    fecha_hasta = st.date_input("Hasta", value=None)
with col3:
    productos = db.get_productos()
    prod_opts = ["Todos"] + [f"[{p[1]}] {p[3]}" for p in productos]
    filtro_prod = st.selectbox("Producto", prod_opts)

tipo_filtro = st.selectbox("Tipo", ["Todos", "compra", "venta", "ajuste", "devolucion", "uso_interno"])

# Construir query con filtros
conn = db.get_connection()
query = """SELECT m.id, m.producto_id, m.tipo, m.cantidad, m.fecha, m.motivo, p.nombre
           FROM movimientos_stock m
           JOIN productos p ON m.producto_id = p.id
           WHERE 1=1"""
params = []

if fecha_desde:
    query += " AND date(m.fecha) >= date(?)"
    params.append(fecha_desde.strftime("%Y-%m-%d"))
if fecha_hasta:
    query += " AND date(m.fecha) <= date(?)"
    params.append(fecha_hasta.strftime("%Y-%m-%d"))
if filtro_prod != "Todos":
    prod_id = next((p[0] for p in productos if f"[{p[1]}] {p[3]}" == filtro_prod), None)
    if prod_id:
        query += " AND m.producto_id = ?"
        params.append(prod_id)
if tipo_filtro != "Todos":
    query += " AND m.tipo = ?"
    params.append(tipo_filtro)

query += " ORDER BY m.fecha DESC LIMIT 200"

movimientos = conn.execute(query, params).fetchall()
conn.close()

if movimientos:
    # Resumen
    total_entradas = sum(m[3] for m in movimientos if m[2] in ('compra', 'devolucion', 'ajuste') and m[3] > 0)
    total_salidas = sum(m[3] for m in movimientos if m[2] in ('venta', 'uso_interno'))
    total_ajustes = sum(m[3] for m in movimientos if m[2] == 'ajuste')
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Entradas (Compras/Dev)", f"{total_entradas:.2f}")
    c2.metric("Salidas (Ventas/Uso)", f"{total_salidas:.2f}")
    c3.metric("Ajustes netos", f"{total_ajustes:+.2f}")
    
    st.divider()
    
    # Tabla
    data = []
    for m in movimientos:
        # m[4] can be datetime or string from SQLite
        if m[4]:
            try:
                fecha_str = m[4].strftime("%d/%m/%Y %H:%M")
            except AttributeError:
                fecha_str = str(m[4])
        else:
            fecha_str = ""
        data.append({
            "Fecha": fecha_str,
            "Producto": m[6],
            "Tipo": m[2].capitalize(),
            "Cantidad": m[3],
            "Motivo": m[5] or "-"
        })
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("No hay movimientos con los filtros seleccionados.")

st.caption("💡 Para registrar compras usa 'Ventas' > tipo 'Compra' o registra entrada. Para ajustes usa la página 'Ajustes de Stock'.")