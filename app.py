import streamlit as st
import database as db
import os
import sys
import time

try:
    import updater
except Exception:
    updater = None

st.set_page_config(
    page_title="Lubricentro Winter",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Lubricentro Winter")
st.markdown("Sistema de gestión de stock y punto de venta")

db.init_db()

# --- Backup automático al iniciar -----------------------------------------
try:
    if os.path.exists("lubricentro.db"):
        db.backup_db()
        db.cleanup_old_backups()
except Exception:
    pass

# --- Chequeo de actualizaciones -------------------------------------------
if updater is not None:
    try:
        update = updater.check_for_update()
    except updater.UpdateError as exc:
        update = None
        st.sidebar.warning(f"No se pudo chequear actualizaciones: {exc}")
    if update:
        with st.sidebar:
            st.markdown("### ⬆️ Actualización disponible")
            st.markdown(
                f"**Versión {update['latest_version']}** (tenés la "
                f"{update['current_version']})"
            )
            if update["release_notes"]:
                with st.expander("Ver notas de la versión"):
                    st.markdown(update["release_notes"])
            if st.button("Descargar actualización", type="primary",
                         key="btn_download_update", use_container_width=True):
                asset = updater.find_asset({"assets": update["assets"]})
                if asset is None:
                    st.error(
                        "No se encontró un archivo descargable en la release. "
                        "Descargala manualmente desde el repositorio."
                    )
                else:
                    progress = st.progress(0.0, text="Descargando...")
                    last_pct = [0.0]

                    def _cb(done: int, total: int) -> None:
                        if total > 0:
                            pct = done / total
                            if pct - last_pct[0] >= 0.01:
                                last_pct[0] = pct
                                progress.progress(pct, text=f"Descargando... {pct:.0%}")

                    try:
                        path = updater.download_asset(asset, progress_callback=_cb)
                        updater.apply_update(path)
                        progress.empty()
                        st.success("Actualización descargada. Reiniciando...")
                        time.sleep(0.5)
                        sys.exit(0)
                    except updater.UpdateError as exc:
                        st.error(f"Error en la descarga: {exc}")

# --- Backup manual en sidebar ---------------------------------------------
with st.sidebar:
    st.markdown("### 💾 Backup de la base de datos")
    if st.button("Crear backup ahora", key="btn_backup_manual",
                 use_container_width=True):
        try:
            path = db.backup_db()
            db.cleanup_old_backups()
            if path:
                st.success(f"Backup creado:\n`{os.path.basename(path)}`")
            else:
                st.warning("No se encontró la base de datos para respaldar.")
        except Exception as exc:
            st.error(f"Error creando backup: {exc}")
    backups_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
    if os.path.isdir(backups_dir):
        backups = [f for f in os.listdir(backups_dir)
                   if f.startswith("lubricentro_backup_") and f.endswith(".db")]
        if backups:
            st.caption(f"Backups guardados: {len(backups)} (se conservan los últimos 10)")
        else:
            st.caption("Aún no hay backups guardados.")

st.divider()

col1, col2, col3 = st.columns(3)

productos = db.get_productos()

with col1:
    st.metric("Productos Activos", len(productos))

with col2:
    valor_inventario = sum(p[10] * p[8] for p in productos)  # precio_venta * stock_actual
    st.metric("Valor Inventario (Precio Venta)", f"${valor_inventario:,.2f}")

with col3:
    stock_critico = sum(1 for p in productos if p[8] <= p[9])  # stock_actual <= stock_minimo
    st.metric("Productos en Stock Crítico", stock_critico)

st.divider()

st.subheader("Últimos Movimientos")
movimientos_recientes = db.get_movimientos(limit=5)
if movimientos_recientes:
    # Mostrar en una tabla pequeña
    data = []
    for m in movimientos_recientes:
        # m: (id, producto_id, tipo, cantidad, fecha, motivo, producto_nombre)
        fecha_str = m[4].strftime("%d/%m/%y %H:%M") if m[4] else ""
        data.append({
            "Fecha": fecha_str,
            "Producto": m[6],
            "Tipo": m[2].capitalize(),
            "Cantidad": m[3],
            "Motivo": (m[5] or "-")[:20] + "..." if m[5] and len(m[5]) > 20 else (m[5] or "-")
        })
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("No hay movimientos recientes.")

st.divider()

st.subheader("Navegación")
st.markdown("""
Usá el menú lateral izquierdo para acceder a las distintas secciones del sistema:

- **Categorías**: Gestión de categorías de productos
- **Proveedores**: Gestión de proveedores y condiciones de pago
- **Productos**: Alta y gestión de productos
- **Movimientos**: Registro de entradas y salidas de stock
- **Clientes**: Gestión de clientes
- **Vehículos**: Gestión de vehículos
- **Servicios**: Gestión de servicios
- **Órdenes de Servicio**: Creación de órdenes de trabajo (servicios y consumo de productos)
- **Reportes**: Reportes de ventas, inventario y balance ingresos vs egresos
""")
