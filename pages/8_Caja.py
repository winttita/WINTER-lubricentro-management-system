import sqlite3
import streamlit as st
import database as db
from style import inject_global_css

st.set_page_config(page_title="Caja", layout="wide")
inject_global_css()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("💰 Caja")

usuario_id = st.session_state.get('user_id')

# --- Estado actual de la caja ---
caja = db.get_caja_abierta()

if caja:
    caja_id = caja[0]
    saldo_inicial = caja[1]
    saldo_actual = caja[2]
    fecha_apertura = caja[3]
    abierta = caja[6]

    st.success(f"✅ Caja abierta #{caja_id}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Saldo Inicial", f"${saldo_inicial:,.2f}")
    with col2:
        st.metric("Saldo Actual", f"${saldo_actual:,.2f}")
    with col3:
        try:
            fecha_str = fecha_apertura.strftime("%d/%m/%Y %H:%M")
        except AttributeError:
            fecha_str = str(fecha_apertura) if fecha_apertura else "-"
        st.metric("Apertura", fecha_str)

    st.divider()

    # --- Registrar ajuste (ingreso/egreso manual) ---
    with st.expander("➕ Registrar ajuste manual"):
        with st.form("ajuste_caja"):
            ajuste_tipo = st.selectbox("Tipo de ajuste", ["Ingreso", "Egreso"])
            monto = st.number_input("Monto", min_value=0.0, step=10.0, format="%.2f")
            observacion = st.text_input("Observación")
            submitted = st.form_submit_button("Registrar ajuste")
            if submitted:
                if monto <= 0:
                    st.error("❌ El monto debe ser mayor a 0.")
                else:
                    if ajuste_tipo == "Egreso":
                        monto = -monto
                    saldo_nuevo = saldo_actual + monto
                    tipo_mov = 'ajuste'
                    ok = db.registrar_movimiento_caja(
                        caja_id, tipo_mov, monto, saldo_actual, saldo_nuevo, observacion, usuario_id
                    )
                    if ok:
                        # Actualizar saldo_actual de la caja
                        conn = db.get_connection()
                        try:
                            conn.execute("UPDATE caja SET saldo_actual = ? WHERE id = ?", (saldo_nuevo, caja_id))
                            conn.commit()
                        finally:
                            conn.close()
                        st.success("✅ Ajuste registrado correctamente.")
                        st.rerun()
                    else:
                        st.error("❌ Error al registrar el ajuste.")

    st.divider()

    # --- Cerrar caja ---
    st.subheader("🔒 Cerrar caja")
    with st.form("cerrar_caja"):
        saldo_final = st.number_input(
            "Saldo final (arqueo real)",
            min_value=0.0,
            value=float(saldo_actual),
            step=10.0,
            format="%.2f"
        )
        diferencia = saldo_final - saldo_actual
        if abs(diferencia) < 0.01:
            st.caption("✅ Coincide con el saldo del sistema.")
        else:
            st.caption(f"⚠️ Diferencia con el sistema: ${diferencia:,.2f}")
        cerrar = st.form_submit_button("Cerrar caja")
        if cerrar:
            try:
                ok = db.cerrar_caja(caja_id, saldo_final, usuario_id)
            except sqlite3.IntegrityError:
                ok = None
            if ok:
                st.success("✅ Caja cerrada correctamente.")
                st.rerun()
            else:
                st.error("❌ No se pudo cerrar la caja.")

else:
    st.warning("⛔ No hay caja abierta.")
    st.subheader("🔓 Abrir caja")
    with st.form("abrir_caja"):
        saldo_inicial = st.number_input(
            "Saldo inicial",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f"
        )
        abrir = st.form_submit_button("Abrir caja")
        if abrir:
            if saldo_inicial < 0:
                st.error("❌ El saldo inicial no puede ser negativo.")
            else:
                try:
                    nuevo_id = db.abrir_caja(float(saldo_inicial), usuario_id)
                except sqlite3.IntegrityError:
                    nuevo_id = None
                if nuevo_id:
                    st.success(f"✅ Caja #{nuevo_id} abierta correctamente.")
                    st.rerun()
                else:
                    st.error("❌ No se pudo abrir la caja.")

st.divider()

# --- Historial de movimientos de caja ---
st.subheader("📋 Historial de movimientos")

col_f1, col_f2 = st.columns(2)
with col_f1:
    fecha_desde = st.date_input("Desde", value=None)
with col_f2:
    tipo_filtro = st.selectbox(
        "Tipo de movimiento",
        ["Todos", "apertura", "cierre", "ajuste", "ingreso_venta"]
    )

conn = db.get_connection()
try:
    query = """
        SELECT mc.id, mc.caja_id, mc.tipo, mc.monto, mc.saldo_anterior,
               mc.saldo_nuevo, mc.observacion, mc.creado_en, u.nombre as usuario_nombre
        FROM movimientos_caja mc
        LEFT JOIN usuarios u ON mc.usuario_id = u.id
        WHERE 1=1
    """
    params = []
    if fecha_desde:
        query += " AND date(mc.creado_en) >= date(?)"
        params.append(fecha_desde)
    if tipo_filtro != "Todos":
        query += " AND mc.tipo = ?"
        params.append(tipo_filtro)
    query += " ORDER BY mc.creado_en DESC LIMIT 200"
    movimientos = conn.execute(query, params).fetchall()
finally:
    conn.close()

if movimientos:
    data = []
    totales = {"ingreso_venta": 0.0, "ajuste": 0.0, "apertura": 0.0, "cierre": 0.0}
    for m in movimientos:
        # m: (id, caja_id, tipo, monto, saldo_anterior, saldo_nuevo, observacion, creado_en, usuario_nombre)
        created = m[7]
        try:
            fecha_str = created.strftime("%d/%m/%Y %H:%M")
        except AttributeError:
            fecha_str = str(created) if created else "-"
        signo = "+" if (m[3] or 0) >= 0 else ""
        data.append({
            "Fecha": fecha_str,
            "Caja #": m[1],
            "Tipo": m[2],
            "Monto": f"{signo}${m[3]:,.2f}",
            "Saldo Anterior": f"${m[4]:,.2f}",
            "Saldo Nuevo": f"${m[5]:,.2f}",
            "Usuario": m[8] or "-",
            "Observación": m[6] or "-",
        })
        totales[m[2]] = totales.get(m[2], 0.0) + float(m[3] or 0)
    st.dataframe(data, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📊 Resumen")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aperturas", f"${totales.get('apertura', 0):,.2f}")
    c2.metric("Ingresos por Venta", f"${totales.get('ingreso_venta', 0):,.2f}")
    c3.metric("Ajustes (neto)", f"${totales.get('ajuste', 0):,.2f}")
    c4.metric("Cierres", f"${totales.get('cierre', 0):,.2f}")
else:
    st.info("ℹ️ No hay movimientos de caja para los filtros seleccionados.")
