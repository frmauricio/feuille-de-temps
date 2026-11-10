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
        background-color: #059669;
        color: #FFFFFF;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Captura del usuario desde la URL
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

# --- ESTRUCTURA DE DÍAS Y SEGUIMIENTO DE LÍNEAS ---
dias = [
    "Dimanche 8 nov", "Lundi 9 nov", "Mardi 10 nov", 
    "Mercredi 11 nov", "Jeudi 12 nov", "Vendredi 13 nov", "Samedi 14 nov"
]

for dia in dias:
    if f"lineas_{dia}" not in st.session_state:
        st.session_state[f"lineas_{dia}"] = [
            {"in": 6.0, "out": 15.5, "abs": "-", "serv": "Service (WO)", "ord": "345924", "loc": "Candiac (Z8)", "comm": ""}
        ]

# --- RENDERIZADO DE ACORDEONES POR DÍA ---
for dia in dias:
    esta_abierto = True if "Lundi" in dia else False
    
    ot_disponible = 3.00 if "Lundi" in dia else 0.00
    rt_disponible = 7.50 if "Lundi" in dia else 0.00

    num_lineas = len(st.session_state[f"lineas_{dia}"])
    label_acordeon = f"{dia}  •  {rt_disponible + ot_disponible:.2f}h RT ({num_lineas} lignes)"

    with st.expander(label_acordeon, expanded=esta_abierto):
        
        lineas_actuales = st.session_state[f"lineas_{dia}"]
        for idx, linea in enumerate(lineas_actuales):
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1, 1.5, 2, 2, 2, 2])
            
            with c1:
                st.number_input("⏰ In", value=linea["in"], step=0.5, key=f"in_{dia}_{idx}")
            with c2:
                st.number_input("⏰ Out", value=linea["out"], step=0.5, key=f"out_{dia}_{idx}")
            with c3:
                st.selectbox("Absence", ["-", "Maladie", "Vacances"], index=0, key=f"abs_{dia}_{idx}")
            with c4:
                st.selectbox("Service", ["Service (WO)", "Interne (WO)", "PM"], index=0, key=f"serv_{dia}_{idx}")
            with c5:
                st.text_input("Order Ref", value=linea["ord"], key=f"ord_{dia}_{idx}")
            with c6:
                st.selectbox("Localisation", ["Candiac (Z8)", "Mirabel", "Saint-Jérôme", "Autre"], index=0, key=f"loc_{dia}_{idx}")
            with c7:
                st.text_input("Commentaire", value=linea["comm"], placeholder="Optionnel", key=f"com_{dia}_{idx}")

        # Resumen y Gestión Dinámica de Overtime
        if ot_disponible > 0:
            st.markdown(
                f"**À confirmer →** <span class='ot-badge'>OT {ot_disponible:.2f}h</span> + <span class='rt-badge'>RT {rt_disponible:.2f}h</span>", 
                unsafe_allow_html=True
            )
            
            key_banco = f"ot_bank_val_{dia}"
            key_pago = f"ot_pay_val_{dia}"
            
            if key_banco not in st.session_state:
                st.session_state[key_banco] = 0.0
            if key_pago not in st.session_state:
                st.session_state[key_pago] = ot_disponible

            def actualizar_pago(d=dia, total=ot_disponible):
                st.session_state[f"ot_pay_val_{d}"] = max(0.0, total - st.session_state[f"ot_bank_val_{d}"])

            def actualizar_banco(d=dia, total=ot_disponible):
                st.session_state[f"ot_bank_val_{d}"] = max(0.0, total - st.session_state[f"ot_pay_val_{d}"])

            aviso_ot = f"⚠️ Shift hors heures standard ({ot_disponible}h hors 08–17h)"
            st.markdown(f"""
                <div style="background-color: #1F2937; border: 1px solid #374151; padding: 12px; border-radius: 8px; color: #F3F4F6; margin-top: 10px; margin-bottom: 10px;">
                    <strong>{aviso_ot}</strong><br>
                    Le client a-t-il demandé de travailler en dehors des heures normales?<br>
                    <small>👉 Répartition des heures d'Overtime disponibles ({ot_disponible}h max) :</small>
                </div>
            """, unsafe_allow_html=True)
            
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                st.number_input(
                    "🏛️ Heures OT en banque", 
                    min_value=0.0, 
                    max_value=ot_disponible, 
                    step=0.5, 
                    key=key_banco,
                    on_change=actualizar_pago
                )
            with col_sel2:
                st.number_input(
                    "💰 Heures OT à payer", 
                    min_value=0.0, 
                    max_value=ot_disponible, 
                    step=0.5, 
                    key=key_pago,
                    on_change=actualizar_banco
                )
        else:
            st.markdown(
                f"**À confirmer →** <span class='rt-badge'>RT {rt_disponible:.2f}h</span>", 
                unsafe_allow_html=True
            )

        # Botones de Acción Diarios
        st.write("")
        c_add, c_del, c_nuit, c_reset = st.columns([2.5, 2.5, 3, 2])
        
        with c_add:
            btn_add_key = f"add_btn_{dia}"
            if st.button("➕ Ajouter", key=btn_add_key, use_container_width=True):
                st.session_state[f"lineas_{dia}"].append(
                    {"in": 8.0, "out":
