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

tab_ventas, tab_inventario, tab_ingr_egr = st.tabs(["Ventas", "Inventario", "Ingresos vs Egresos"])

with tab_ventas:
    st.subheader(f"Reporte de Ventas - {periodo}")
    ventas = db.get_reporte_ventas(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    if ventas:
        df = pd.DataFrame(ventas, columns=["Fecha", "Tipo", "Concepto", "Cantidad", "Monto"])
        df["Monto"] = df["Monto"].astype(float)
        c1, c2, c3 = st.columns(3)
        c1.metric("Transacciones", len(df))
        c2.metric("Items vendidos", df["Cantidad"].sum())
        c3.metric("Total vendido", f"${df['Monto'].sum():,.2f}")
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
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
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
        st.markdown("#### Ingresos (Ordenes de servicio)")
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
