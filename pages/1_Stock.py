import streamlit as st
import database as db
from datetime import date
from style import inject_global_css

st.set_page_config(page_title="Stock", layout="wide")
inject_global_css()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("📦 Stock")

tab_stock, tab_mov, tab_adj = st.tabs(["Stock Actual", "Movimientos", "Ajustes"])


# =============================================================================
# Tab 1: Stock Actual
# =============================================================================
with tab_stock:
    st.subheader("Inventario actual")

    busqueda = st.text_input("Buscar producto", placeholder="Nombre, código interno o código de barras...", key="stock_search")

    inventario = db.get_reporte_inventario()
    productos = db.get_productos()

    if not productos:
        st.info("No hay productos cargados.")
    else:
        busqueda_lower = busqueda.strip().lower()
        if busqueda_lower:
            inventario = [i for i in inventario if busqueda_lower in (i[1] or '').lower()]

        st.metric("Productos activos", len(inventario))

        data = []
        total_unidades = 0
        valor_costo_total = 0.0
        valor_venta_total = 0.0
        for i in inventario:
            pid, nombre, stock_actual, stock_minimo, precio_costo, precio_venta, categoria, valor_costo, valor_venta = i
            total_unidades += stock_actual
            valor_costo_total += valor_costo or 0
            valor_venta_total += valor_venta or 0
            critico = "⚠️" if stock_actual <= stock_minimo else ""
            data.append({
                "ID": pid,
                "Nombre": nombre,
                "Categoría": categoria or "-",
                "Stock Actual": stock_actual,
                "Stock Mínimo": stock_minimo,
                "Precio Costo": f"${precio_costo:.2f}",
                "Precio Venta": f"${precio_venta:.2f}",
                "Valor Costo": f"${valor_costo:.2f}",
                "Valor Venta": f"${valor_venta:.2f}",
                "Stock Crítico": critico,
            })

        c1, c2, c3 = st.columns(3)
        c1.metric("Total unidades en stock", f"{total_unidades:.0f}")
        c2.metric("Valor al costo", f"${valor_costo_total:,.2f}")
        c3.metric("Valor a la venta", f"${valor_venta_total:,.2f}")

        st.dataframe(data, use_container_width=True, hide_index=True)

        bajos = [d for d in data if d["Stock Crítico"] == "⚠️"]
        if bajos:
            st.warning(f"⚠️ {len(bajos)} productos bajo stock mínimo")


# =============================================================================
# Tab 2: Movimientos
# =============================================================================
with tab_mov:
    st.subheader("Historial de Movimientos de Stock")

    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_desde = st.date_input("Desde", value=None, key="mov_fd")
    with col2:
        fecha_hasta = st.date_input("Hasta", value=None, key="mov_fh")
    with col3:
        prod_opts = ["Todos"] + [f"[{p[1]}] {p[3]}" for p in productos]
        filtro_prod = st.selectbox("Producto", prod_opts, key="mov_prod")

    tipo_filtro = st.selectbox("Tipo", ["Todos", "compra", "venta", "ajuste", "devolucion", "uso_interno"], key="mov_tipo")

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
        total_entradas = sum(m[3] for m in movimientos if m[2] in ('compra', 'devolucion') and m[3] > 0)
        total_salidas = sum(m[3] for m in movimientos if m[2] in ('venta', 'uso_interno') and m[3] > 0)
        total_ajustes = sum(m[3] for m in movimientos if m[2] == 'ajuste')

        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas (Compras/Dev)", f"{total_entradas:.2f}")
        c2.metric("Salidas (Ventas/Uso)", f"{total_salidas:.2f}")
        c3.metric("Ajustes netos", f"{total_ajustes:+.2f}")

        st.divider()

        data = []
        for m in movimientos:
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


# =============================================================================
# Tab 3: Ajustes
# =============================================================================
with tab_adj:
    st.subheader("Ajustes de Stock")
    st.caption("Solo administradores y supervisores pueden hacer ajustes. Motivo obligatorio.")

    if st.session_state.get('user_rol') not in ('admin', 'supervisor'):
        st.error("No tenés permisos para hacer ajustes de stock.")
    else:
        prod_opts_adj = {f"[{p[1]}] {p[3]} - Stock: {p[8]}": p[0] for p in productos}

        with st.form("ajuste_form"):
            col1, col2 = st.columns(2)
            with col1:
                prod_sel = st.selectbox("Producto", list(prod_opts_adj.keys()), key="adj_prod")
                producto_id = prod_opts_adj[prod_sel]

                prod_info = next((p for p in productos if p[0] == producto_id), None)
                stock_actual = float(prod_info[8]) if prod_info else 0.0
                st.info(f"Stock actual: **{stock_actual}**")

            with col2:
                stock_nuevo = st.number_input("Nuevo stock", min_value=0.0, value=stock_actual, step=1.0, key="adj_nuevo")
                motivo = st.text_area("Motivo *", placeholder="Ej: Rotura, merma, inventario físico, error de carga...", height=100, key="adj_motivo")

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
                            st.success(f"Ajuste aplicado: {stock_actual} → {stock_nuevo} ({diff:+.2f})")
                            st.rerun()
                        else:
                            st.error("Error al aplicar ajuste.")

    st.divider()

    st.subheader("Historial de Ajustes")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        fd = st.date_input("Desde", value=None, key="adj_fd")
    with col_f2:
        fh = st.date_input("Hasta", value=None, key="adj_fh")
    with col_f3:
        prod_filtro = st.selectbox("Filtrar producto", ["Todos"] + list(prod_opts_adj.keys()), key="adj_filtro_prod")

    if st.button("Buscar ajustes", key="adj_btn"):
        fd_str = fd.strftime("%Y-%m-%d") if fd else None
        fh_str = fh.strftime("%Y-%m-%d") if fh else None
        pid = prod_opts_adj.get(prod_filtro) if prod_filtro != "Todos" else None

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
            st.info("No hay ajustes con esos filtros.")
