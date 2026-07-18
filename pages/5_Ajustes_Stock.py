import streamlit as st
import database as db
from datetime import date

st.set_page_config(page_title="Ajustes de Stock", layout="wide")
st.title("⚙️ Ajustes de Stock")

st.caption("Solo supervisores y administradores pueden hacer ajustes. Registra motivo obligatorio.")

# Usuario temporal (hasta login)
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1
    st.session_state.user_rol = 'admin'

# Solo permitir si es admin o supervisor
if st.session_state.user_rol not in ('admin', 'supervisor'):
    st.error("🚫 No tenés permisos para acceder a esta página")
    st.stop()

# --- Formulario de Ajuste ---
st.subheader("Nuevo Ajuste")

productos = db.get_productos()
prod_opts = {f"[{p[1]}] {p[3]} - Stock: {p[8]}": p[0] for p in productos}

with st.form("ajuste_form"):
    col1, col2 = st.columns(2)
    with col1:
        prod_sel = st.selectbox("Producto", list(prod_opts.keys()))
        producto_id = prod_opts[prod_sel]
        
        # Mostrar stock actual
        prod_info = next((p for p in productos if p[0] == producto_id), None)
        if prod_info:
            st.info(f"Stock actual: **{prod_info[8]}**")
            stock_actual = float(prod_info[8])
    
    with col2:
        stock_nuevo = st.number_input("Nuevo stock", min_value=0.0, value=stock_actual, step=1.0)
        motivo = st.text_area("Motivo *", placeholder="Ej: Rotura, merma, inventario físico, error de carga...", height=100)
    
    submitted = st.form_submit_button("Aplicar Ajuste", type="primary")
    
    if submitted:
        if not motivo.strip():
            st.error("El motivo es obligatorio")
        else:
            diff = stock_nuevo - stock_actual
            if diff == 0:
                st.warning("El stock no cambió")
            else:
                ok = db.crear_ajuste_stock(producto_id, stock_nuevo, motivo.strip(), st.session_state.user_id)
                if ok:
                    st.success(f"✅ Ajuste aplicado: {stock_actual} → {stock_nuevo} ({diff:+.2f})")
                    st.rerun()
                else:
                    st.error("Error al aplicar ajuste")

st.divider()

# --- Historial de Ajustes ---
st.subheader("Historial de Ajustes")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    fd = st.date_input("Desde", value=None, key="adj_fd")
with col_f2:
    fh = st.date_input("Hasta", value=None, key="adj_fh")
with col_f3:
    prod_filtro = st.selectbox("Filtrar producto", ["Todos"] + list(prod_opts.keys()))

if st.button("Buscar"):
    fd_str = fd.strftime("%Y-%m-%d") if fd else None
    fh_str = fh.strftime("%Y-%m-%d") if fh else None
    pid = prod_opts.get(prod_filtro) if prod_filtro != "Todos" else None
    
    ajustes = db.get_ajustes_stock(limit=100, fecha_desde=fd_str, fecha_hasta=fh_str, producto_id=pid)
    
    if ajustes:
        data = []
        for a in ajustes:
            fecha_str = a[7].strftime("%d/%m/%Y %H:%M") if a[7] else ""
            data.append({
                "Fecha": fecha_str,
                "Producto": a[8],
                "Stock Ant.": a[2],
                "Stock Nvo.": a[3],
                "Diferencia": a[4],
                "Motivo": a[5],
                "Usuario": a[9]
            })
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("No hay ajustes con esos filtros")