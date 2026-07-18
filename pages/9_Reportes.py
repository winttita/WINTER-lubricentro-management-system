import streamlit as st
import database as db
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Reportes", layout="wide")

st.title("Reportes")

st.sidebar.header("Filtros")
periodo = st.sidebar.selectbox("Periodo", ["Hoy", "Últimos 7 días", "Últimos 30 días", "Este mes", "Todo"])
hoy = datetime.now().date()
if periodo == "Hoy":
    fecha_desde, fecha_hasta = hoy, hoy
elif periodo == "Últimos 7 días":
    fecha_desde, fecha_hasta = hoy - timedelta(days=7), hoy
elif periodo == "Últimos 30 días":
    fecha_desde, fecha_hasta = hoy - timedelta(days=30), hoy
elif periodo == "Este mes":
    fecha_desde = hoy.replace(day=1)
    fecha_hasta = hoy
else:
    fecha_desde, fecha_hasta = None, None

fd = fecha_desde.strftime("%Y-%m-%d") if fecha_desde else None
fh = fecha_hasta.strftime("%Y-%m-%d") if fecha_hasta else None

tab_ventas, tab_inventario, tab_ingr_egr, tab_cc = st.tabs(["Ventas", "Inventario", "Ingresos vs Egresos", "Cta. Corriente"])

with tab_ventas:
    st.subheader(f"Reporte de Ventas - {periodo}")
    # Usar la nueva función que incluye ventas + ordenes
    ventas = db.get_reporte_ventas_detallado(fecha_desde=fd, fecha_hasta=fh)
    if ventas:
        df = pd.DataFrame(ventas, columns=[
            "Venta ID", "Fecha", "Tipo Comp.", "Punto Vta", "Número",
            "Subtotal", "IVA", "Total", "Método Pago", "Cliente",
            "Prod. ID", "Producto", "Cant.", "Precio Unit.", "Subtotal Item"
        ])
        for col in ["Subtotal", "IVA", "Total", "Precio Unit.", "Subtotal Item"]:
            if col in df.columns:
                df[col] = df[col].astype(float)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Comprobantes", df["Venta ID"].nunique())
        c2.metric("Items vendidos", df["Cant."].sum())
        c3.metric("Total con IVA", f"${df['Total'].sum():,.2f}")
        c4.metric("Subtotal", f"${df['Subtotal'].sum():,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay ventas en el periodo seleccionado.")

with tab_inventario:
    st.subheader("Inventario actual")
    inventario = db.get_reporte_inventario()
    if inventario:
        df = pd.DataFrame(inventario, columns=[
            "ID", "Nombre", "Stock Actual", "Stock Mínimo",
            "Precio Costo", "Precio Venta", "Categoría",
            "Valor Costo", "Valor Venta"
        ])
        df["Valor Costo"] = df["Valor Costo"].astype(float)
        df["Valor Venta"] = df["Valor Venta"].astype(float)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Productos activos", len(df))
        c2.metric("Total unidades en stock", df["Stock Actual"].sum())
        c3.metric("Valor al costo", f"${df['Valor Costo'].sum():,.2f}")
        c4.metric("Valor a la venta", f"${df['Valor Venta'].sum():,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.divider()
        st.markdown("### Productos bajo stock mínimo")
        bajos = df[df["Stock Actual"] < df["Stock Mínimo"]][["Nombre", "Stock Actual", "Stock Mínimo"]]
        if bajos.empty:
            st.success("Todos los productos están por encima del stock mínimo")
        else:
            st.dataframe(bajos, use_container_width=True, hide_index=True)
    else:
        st.info("No hay productos activos.")

with tab_ingr_egr:
    st.subheader(f"Ingresos vs Egresos - {periodo}")
    ingresos, egresos = db.get_reporte_ingresos_egresos(
        fecha_desde=fd, fecha_hasta=fh
    )
    total_ingresos = sum(i[1] or 0 for i in ingresos)
    total_egresos = sum(e[2] or 0 for e in egresos)
    balance = total_ingresos - total_egresos
    c1, c2, c3 = st.columns(3)
    c1.metric("Total ingresos", f"${total_ingresos:,.2f}")
    c2.metric("Total egresos", f"${total_egresos:,.2f}")
    c3.metric("Balance", f"${balance:,.2f}", delta="Positivo" if balance >= 0 else "Negativo")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Ingresos (Órdenes de servicio)")
        if ingresos:
            df_i = pd.DataFrame(
                [{"Fecha": i[2], "Cliente": i[0], "Monto": i[1]} for i in ingresos]
            )
            st.dataframe(df_i, use_container_width=True, hide_index=True)
        else:
            st.info("Sin ingresos en el periodo.")
    with col2:
        st.markdown("#### Egresos (Compras de stock)")
        if egresos:
            df_e = pd.DataFrame(
                [{"Fecha": e[3], "Producto": e[0], "Cantidad": e[1], "Monto": e[2]} for e in egresos]
            )
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        else:
            st.info("Sin egresos en el periodo.")

with tab_cc:
    st.subheader("Clientes con Cuenta Corriente")
    clientes_deuda = db.get_clientes_con_deuda()
    if clientes_deuda:
        df_cc = pd.DataFrame(clientes_deuda, columns=["ID", "Nombre", "Teléfono", "Email", "Deuda Total"])
        df_cc["Deuda Total"] = df_cc["Deuda Total"].astype(float)
        st.dataframe(df_cc, use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("### Detalle de movimientos")
        cliente_sel = st.selectbox("Ver movimientos de:", ["Seleccionar..."] + [c[1] for c in clientes_deuda])
        if cliente_sel != "Seleccionar...":
            cli_id = next(c[0] for c in clientes_deuda if c[1] == cliente_sel)
            movs = db.get_movimientos_cuenta_corriente(cli_id)
            if movs:
                df_m = pd.DataFrame(movs, columns=["ID", "Venta ID", "Monto", "Saldo Ant.", "Saldo Nvo.", "Fecha", "Tipo Comp.", "Punto Vta", "Número"])
                st.dataframe(df_m, use_container_width=True, hide_index=True)
            else:
                st.info("Sin movimientos")
    else:
        st.info("No hay clientes con deuda.")