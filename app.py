import streamlit as st
import os
import time
import database as db
from updater import APP_VERSION, check_for_update
from style import inject_global_css

st.set_page_config(
    page_title="Centro Automotor WINTER",
    page_icon="🔧",
    layout="wide"
)

inject_global_css()

db.init_db()

# Backup automático al arrancar (silencioso: si falla, no bloquea la app).
# cleanup_old_backups mantiene solo los últimos 10 backups.
try:
    db.backup_db()
    db.cleanup_old_backups()
except Exception:
    pass


# --- Helpers de sesión ---
def init_session():
    """Inicializa flags de sesión si no existen."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_nombre' not in st.session_state:
        st.session_state.user_nombre = None
    if 'user_rol' not in st.session_state:
        st.session_state.user_rol = None


def cerrar_sesion():
    """Limpia el estado de sesión."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_nombre = None
    st.session_state.user_rol = None


init_session()


# --- Pantalla de Login ---
if not st.session_state.logged_in:
    st.image("centro_automotor.png", width=250)
    st.markdown("## Centro Automotor WINTER")
    st.markdown("### Iniciar sesión")
    st.divider()

    col_login, col_spacer = st.columns([2, 3])
    with col_login:
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Ingresá usuario y contraseña.")
                else:
                    user = db.verificar_login(username.strip(), password)
                    if user is None:
                        st.error("Credenciales incorrectas o usuario inactivo.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["user_id"]
                        st.session_state.user_nombre = user["nombre"]
                        st.session_state.user_rol = user["rol"]
                        st.rerun()

    # st.caption("Usuario por defecto: **admin** | Contraseña: **winter1234**")
    st.stop()


# --- App principal (solo si estás logueado) ---
st.image("centro_automotor.png", width=300)
st.title("Centro Automotor WINTER")
st.markdown(f"Bienvenido, **{st.session_state.user_nombre}**")
st.markdown("Sistema de gestión de stock y punto de venta")

# --- Sidebar: usuario + logout + actualizaciones ---
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.user_nombre}**")
    st.caption(f"Rol: {st.session_state.user_rol}")
    if st.button("Cerrar sesión", use_container_width=True):
        cerrar_sesion()
        st.rerun()

    st.divider()
    st.caption(f"Versión {APP_VERSION}")
    update_info = None
    try:
        update_info = check_for_update()
    except Exception as e:
        st.caption(f"⚠️ No se pudo verificar actualizaciones: {e}")
    if update_info:
        st.warning(f"⬆️ Actualización disponible: **v{update_info['latest_version']}**")
        if st.button("Descargar e instalar actualización", use_container_width=True):
            from updater import download_asset, find_asset, apply_update
            asset = find_asset({"assets": update_info["assets"]})
            if asset:
                total_size = asset.get("size", 0) or 0
                progress_bar = st.progress(0.0, text="Iniciando descarga...")
                eta_text = st.empty()
                start_ts = time.monotonic()
                rate_window = []

                def _cb(done, total):
                    elapsed = time.monotonic() - start_ts
                    if total:
                        frac = done / total
                        if elapsed > 0.3 and done > 0:
                            rate = done / elapsed
                            rate_window.append(rate)
                            if len(rate_window) > 5:
                                rate_window.pop(0)
                            avg = sum(rate_window) / len(rate_window)
                            remaining = (total - done) / avg
                            eta_text.markdown(
                                f"**{frac*100:.1f}%** · ~{int(remaining)}s restantes · "
                                f"{avg/1024/1024:.1f} MB/s"
                            )
                        progress_bar.progress(
                            min(frac, 1.0),
                            text=f"{done/1024/1024:.1f} / {total/1024/1024:.1f} MB",
                        )
                    else:
                        progress_bar.progress(
                            min(done / (300 * 1024 * 1024), 1.0),
                            text=f"{done/1024/1024:.1f} MB (tamaño desconocido)",
                        )

                try:
                    path = download_asset(asset, progress_callback=_cb)
                except Exception as e:
                    st.error(f"❌ Error al descargar actualización: {e}")
                    st.stop()
                progress_bar.progress(1.0, text="Descarga completa.")
                eta_text.empty()
                try:
                    db.backup_db()
                except Exception:
                    pass
                try:
                    apply_update(path)
                except Exception as e:
                    st.error(f"❌ Error al preparar la actualización: {e}")
                    st.stop()
                st.success("✅ Actualización lista. La app se cerrará y reiniciará.")
                time.sleep(2)
                os._exit(0)
            else:
                st.error("❌ No se encontró el asset de actualización")
    else:
        st.caption("✅ Última versión")

st.divider()

col1, col2, col3 = st.columns(3)

productos = db.get_productos()

with col1:
    st.metric("Productos Activos", len(productos))

with col2:
    valor_inventario = sum(p[10] * p[7] for p in productos)  # precio_venta * stock_actual
    st.metric("Valor Inventario (Precio Venta)", f"${valor_inventario:,.2f}")

with col3:
    stock_critico = sum(1 for p in productos if p[7] <= p[8])  # stock_actual <= stock_minimo
    st.metric("Productos en Stock Crítico", stock_critico)

st.divider()

st.subheader("Últimos Movimientos")
movimientos_recientes = db.get_movimientos(limit=5)
if movimientos_recientes:
    # Mostrar en una tabla pequeña
    data = []
    for m in movimientos_recientes:
        # m: (id, producto_id, tipo, cantidad, fecha, motivo, producto_nombre)
        # m[4] can be datetime or string from SQLite
        fecha_raw = m[4]
        if fecha_raw:
            try:
                # Try to parse as datetime object first (if SQLite returned datetime)
                if hasattr(fecha_raw, 'strftime'):
                    fecha_str = fecha_raw.strftime("%d/%m/%y %H:%M")
                else:
                    # Parse ISO format string from SQLite
                    from datetime import datetime
                    if isinstance(fecha_raw, str):
                        # Handle possible formats: "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD HH:MM:SS.ssssss"
                        try:
                            dt = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                dt = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S.%f")
                            except ValueError:
                                dt = datetime.strptime(fecha_raw, "%Y-%m-%d")
                        fecha_str = dt.strftime("%d/%m/%y %H:%M")
                    else:
                        fecha_str = str(fecha_raw)
            except Exception:
                fecha_str = str(fecha_raw)
        else:
            fecha_str = ""
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

- **Gestión**: Clientes, vehículos, proveedores y servicios
- **Productos**: Categorías, alta y gestión de productos
- **Stock**: Inventario actual, movimientos y ajustes de stock
- **Ventas**: Punto de venta
- **Compras**: Compras a proveedores
- **Cuenta Corriente**: Saldos y pagos de clientes
- **Órdenes de Servicio**: Creación de órdenes de trabajo (servicios y consumo de productos)
- **Reportes**: Reportes de ventas, inventario y balance ingresos vs egresos
""")
