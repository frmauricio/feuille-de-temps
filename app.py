import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. Configuración de la página
st.set_page_config(
    page_title="Feuille de temps — BMS",
    page_icon="📅",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div[data-testid="stExpander"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .ot-badge {
        background-color: #D97706;
        color: #FFFFFF;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .rt-badge {
