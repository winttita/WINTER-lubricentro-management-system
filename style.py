import streamlit as st


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
