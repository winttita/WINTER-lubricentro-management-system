import streamlit as st
import database as db
from datetime import datetime
from style import inject_global_css

st.set_page_config(page_title="Cuenta Corriente", layout="wide")
inject_global_css()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Debe iniciar sesión para acceder a esta página.")
    st.stop()

st.title("💰 Cuenta Corriente")

# --- Resumen general ---
deudores = db.get_clientes_con_deuda()
deuda_total = sum(d[4] for d in deudores) if deudores else 0.0
cant_deudores = len(deudores) if deudores else 0
mayor_deuda = max(deudores, key=lambda d: d[4]) if deudores else None

c1, c2, c3 = st.columns(3)
c1.metric("Clientes con deuda", cant_deudores)
c2.metric("Deuda total consolidada", f"${deuda_total:,.2f}")
if mayor_deuda:
    c3.metric("Mayor deuda", f"${mayor_deuda[4]:,.2f}", delta=mayor_deuda[1])
else:
    c3.metric("Mayor deuda", "$0.00")

st.divider()

# --- Clientes con deuda ---
st.subheader("📋 Clientes con deuda")

if deudores:
    data = []
    for d in deudores:
        # d: (id, nombre, telefono, email, deuda_total, antiguedad_dias, ultimo_movimiento)
        antiguedad = d[5] if len(d) > 5 else 0
        ultimo = d[6] if len(d) > 6 else None
        if ultimo:
            try:
                ultimo_str = ultimo.strftime("%d/%m/%Y %H:%M") if hasattr(ultimo, 'strftime') else str(ultimo)
            except Exception:
                ultimo_str = str(ultimo)
        else:
            ultimo_str = "-"

        # Color code antigüedad
        if antiguedad is None:
            antiguedad_label = "-"
        elif antiguedad <= 7:
            antiguedad_label = f"{antiguedad} días"
        elif antiguedad <= 30:
            antiguedad_label = f"⚠️ {antiguedad} días"
        else:
            antiguedad_label = f"🔴 {antiguedad} días"

        data.append({
            "ID": d[0],
            "Cliente": d[1],
            "Teléfono": d[2] or "-",
            "Email": d[3] or "-",
            "Deuda": f"${d[4]:,.2f}",
            "Antigüedad": antiguedad_label,
            "Último movimiento": ultimo_str,
        })
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.success("No hay clientes con deuda pendiente.")

st.divider()

# --- Detalle por cliente + Registrar pago ---
st.subheader("🔍 Detalle y Pagos")

clientes = db.get_clientes()
if not clientes:
    st.info("No hay clientes cargados.")
    st.stop()

cliente_ops = {c[1]: c[0] for c in clientes}
col_sel, col_saldo = st.columns([3, 1])
with col_sel:
    cliente_sel = st.selectbox("Seleccionar cliente", list(cliente_ops.keys()))
with col_saldo:
    if cliente_sel:
        saldo = db.get_cuenta_corriente_cliente(cliente_ops[cliente_sel])
        if saldo > 0:
            st.metric("Saldo actual", f"${saldo:,.2f}")
        else:
            st.metric("Saldo actual", "$0.00")

if cliente_sel:
    cli_id = cliente_ops[cliente_sel]

    # --- Registrar pago ---
    with st.expander("💸 Registrar pago", expanded=(saldo > 0 if cliente_sel else False)):
        # Mostrar tickets pendientes del cliente
        tickets_pendientes = db.get_ventas_pendientes_cc(cli_id) if saldo > 0 else []
        ventas_sel_ids = []
        monto_sugerido = 0.0

        if tickets_pendientes:
            st.markdown("**Tickets pendientes de pago**")
            ticket_opts = []
            for t in tickets_pendientes:
                # t: (venta_id, tipo_comprobante, punto_venta, numero, total, ya_pagado, pendiente)
                etiqueta = f"{t[1].upper()} {t[2]}-{t[3]:08d} - Pendiente: ${t[6]:.2f}"
                ticket_opts.append((etiqueta, t[0], t[6]))

            # Checkbox por ticket
            for etiqueta, vid, pend in ticket_opts:
                if st.checkbox(etiqueta, key=f"chk_pag_{vid}"):
                    ventas_sel_ids.append(vid)
                    monto_sugerido += pend

            if ventas_sel_ids:
                st.info(f"Tickets seleccionados: {len(ventas_sel_ids)} | Total a pagar: ${monto_sugerido:.2f}")
            st.divider()
        else:
            if saldo > 0:
                st.caption("No hay tickets individuales pendientes (saldo residual).")

        with st.form("pago_form"):
            p1, p2 = st.columns(2)
            with p1:
                monto_pago = st.number_input(
                    "Monto a pagar *",
                    min_value=0.0,
                    value=monto_sugerido if monto_sugerido > 0 else 0.0,
                    step=0.01,
                    format="%.2f"
                )
            with p2:
                metodos_pago = ["efectivo", "tarjeta", "transferencia"]
                metodo_sel = st.selectbox("Método de pago", metodos_pago)
            observacion = st.text_input("Observación", placeholder="Ej: Pago parcial, adelanto, etc.")

            if st.form_submit_button("Registrar pago", type="primary"):
                if monto_pago <= 0:
                    st.error("El monto debe ser mayor a 0.")
                else:
                    if ventas_sel_ids:
                        ok = db.registrar_pago_cc_con_ventas(cli_id, monto_pago, metodo_sel, observacion, st.session_state.user_id, venta_ids=ventas_sel_ids)
                    else:
                        ok = db.registrar_pago_cc(cli_id, monto_pago, metodo_sel, observacion, st.session_state.user_id)
                    if ok:
                        st.success(f"Pago de ${monto_pago:.2f} registrado correctamente.")
                        # Limpiar selección de tickets reseteando el form
                        st.rerun()
                    else:
                        st.error("Error al registrar el pago.")

    # --- Movimientos del cliente ---
    st.markdown("#### Movimientos")
    movimientos = db.get_movimientos_cuenta_corriente(cli_id)
    if movimientos:
        mov_data = []
        for m in movimientos:
            # m: (id, venta_id, monto, saldo_anterior, saldo_nuevo, creado_en,
            #     tipo_comprobante, punto_venta, numero_comprobante,
            #     tipo_movimiento, metodo_pago, observacion)
            fecha = m[5]
            if fecha:
                try:
                    fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if hasattr(fecha, 'strftime') else str(fecha)
                except Exception:
                    fecha_str = str(fecha)
            else:
                fecha_str = "-"

            tipo_mov = m[9] if len(m) > 9 else 'venta'
            monto = m[2]
            if tipo_mov == 'venta':
                desc = f"Venta #{m[1]}" if m[1] else "Venta"
                comp = f"{m[6].upper()} {m[7]}-{m[8]:08d}" if m[6] else f"#{m[1]}"
                desc = comp
                monto_str = f"+${monto:,.2f}"
            else:
                desc = "Pago"
                monto_str = f"-${abs(monto):,.2f}"

            mov_data.append({
                "Fecha": fecha_str,
                "Tipo": tipo_mov.capitalize(),
                "Descripción": desc,
                "Monto": monto_str,
                "Saldo anterior": f"${m[3]:,.2f}",
                "Saldo nuevo": f"${m[4]:,.2f}",
                "Método": (m[10] or "-") if len(m) > 10 else "-",
                "Observación": (m[11] or "-") if len(m) > 11 else "-",
            })
        st.dataframe(mov_data, use_container_width=True, hide_index=True)
    else:
        st.info("Este cliente no tiene movimientos en cuenta corriente.")
