import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# 1. Configuración de la página en modo oscuro / ancho
st.set_page_config(
    page_title="Feuille de temps — BMS",
    page_icon="📅",
    layout="wide"
)

# Estilos CSS para imitar la estética oscura y refinada de la captura
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
        background-color: #059669;
        color: #FFFFFF;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Captura de parámetros URL (para detectar automáticamente al técnico)
query_params = st.query_params
emp_code = query_params.get("emp", "Fredy Diaz")

# --- SECCIÓN SUPERIOR: PÉRIODE ---
st.title("📅 Période")

col_prev, col_today, col_next, col_date_range = st.columns([1, 1, 1, 3])

with col_prev:
    st.button("◄", use_container_width=True)
with col_today:
    st.button("Auj.", use_container_width=True)
with col_next:
    st.button("►", use_container_width=True)
with col_date_range:
    st.date_input(
        "Rango de Fechas", 
        value=(date(2026, 11, 8), date(2026, 11, 14)), 
        label_visibility="collapsed"
    )

col_btn1, col_btn2, col_spacer = st.columns([1.5, 2, 4.5])
with col_btn1:
    st.button("🔄 Rafraîchir", use_container_width=True)
with col_btn2:
    st.button("🏖️ Semaine en vacances", use_container_width=True)

st.markdown(f"### Saisie des heures — {emp_code}")
st.divider()

# --- SECCIÓN DE DÍAS (ACORDEONES) ---
dias_semana = [
    ("Dimanche 8 nov", False, 0.0, 0.0),
    ("Lundi 9 nov", True, 7.5, 2.0),
    ("Mardi 10 nov", False, 0.0, 0.0),
    ("Mercredi 11 nov", False, 0.0, 0.0),
    ("Jeudi 12 nov", False, 0.0, 0.0),
    ("Vendredi 13 nov", False, 0.0, 0.0),
    ("Samedi 14 nov", False, 0.0, 0.0)
]

# Inicializar sesión para guardar líneas de tiempo si no existen
if "filas_lunes" not in st.session_state:
    st.session_state.filas_lunes = [
        {"in": 6.0, "out": 15.5, "absence": "-", "service": "Service (WO)", "order": "345924", "loc": "Candiac (Z8)", "comm": ""}
    ]

for nombre_dia, esta_abierto, rt_val, ot_val in dias_semana:
    
    # Título dinámico del acordeón con badges de OT (Overtime) si existen
    label_acordeon = nombre_dia
    if ot_val > 0:
        label_acordeon += f"  🟡 {ot_val + rt_val:.2f}h OT"

    with st.expander(label_acordeon, expanded=esta_abierto):
        
        # Renderizar cada fila de entrada de tiempo dentro del día
        for idx, fila in enumerate(st.session_state.filas_lunes if "Lundi" in nombre_dia else [1]):
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1, 1.5, 2, 2, 2, 2])
            
            with c1:
                st.number_input("⏰ In", value=6.0, step=0.5, key=f"in_{nombre_dia}_{idx}")
            with c2:
                st.number_input("⏰ Out", value=15.5, step=0.5, key=f"out_{nombre_dia}_{idx}")
            with c3:
                st.selectbox("Absence", ["-", "Maladie", "Vacances"], key=f"abs_{nombre_dia}_{idx}")
            with c4:
                st.selectbox("Service", ["Service (WO)", "Interne (WO)", "PM"], key=f"serv_{nombre_dia}_{idx}")
            with c5:
                st.text_input("Order Ref", value="Ex: 345924", key=f"ord_{nombre_dia}_{idx}")
            with c6:
                st.selectbox("Localisation", ["Candiac (Z8)", "Mirabel", "Saint-Jérôme", "Autre"], key=f"loc_{nombre_dia}_{idx}")
            with c7:
                st.text_input("Commentaire", placeholder="Optionnel", key=f"com_{nombre_dia}_{idx}")

        # Cálculo dinámico en el footer del día
        if "Lundi" in nombre_dia:
            st.markdown(
                f"**À confirmer →** <span class='ot-badge'>OT 2.00h</span> + <span class='rt-badge'>RT 7.50h</span>", 
                unsafe_allow_html=True
            )
            
            st.write("")
            c_add, c_nuit, c_reset = st.columns([2, 3, 2])
            with c_add:
                st.button("➕ Ajouter une ligne", key=f"add_{nombre_dia}", use_container_width=True)
            with c_nuit:
                st.button("🌙 Nuit à l'extérieur", key=f"nuit_{nombre_dia}", use_container_width=True)
            with c_reset:
                st.button("🗑️ Réinitialiser", key=f"reset_{nombre_dia}", use_container_width=True)
