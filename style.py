import os

import streamlit as st

LOGO_FILENAME = "centro_automotor.png"


def get_logo_path():
    """Devuelve la ruta absoluta del logo si existe, o None.

    Busca en el directorio de trabajo actual y en el directorio de este
    modulo (cubre el layout empaquetado donde el png queda junto al exe).
    """
    candidates = [
        os.path.join(os.getcwd(), LOGO_FILENAME),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGO_FILENAME),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return None


def inject_global_css():
    """Inyecta CSS para ocultar el mensaje 'Press Enter to submit form' de Streamlit."""
    st.markdown("""
    <style>
    /* Ocultar 'Press Enter to submit form' en formularios */
    div[data-testid="stForm"] small { display: none !important; }
    /* Streamlit 1.30+ usa .st-emotion-cache-* */
    .st-emotion-cache-1v0p1ee, .st-emotion-cache-ll22cq { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


def flash_exito(mensaje):
    """Guarda un mensaje de exito para mostrar en el proximo render."""
    st.session_state["flash"] = ("success", mensaje)
    st.toast(mensaje)


def flash_error(mensaje):
    """Guarda un mensaje de error para mostrar en el proximo render."""
    st.session_state["flash"] = ("error", mensaje)


def mostrar_flash():
    """Muestra el mensaje flash pendiente (exito/error) y lo limpia."""
    if "flash" in st.session_state and st.session_state["flash"]:
        tipo, mensaje = st.session_state["flash"]
        if tipo == "success":
            st.success(mensaje)
        elif tipo == "error":
            st.error(mensaje)
        st.session_state["flash"] = None
