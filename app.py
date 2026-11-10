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

# 2. Funciones de actualización para el Overtime
def make_update_pago(d, total):
    def callback():
        st.session_state[f"ot_pay_val_{d}"] = max(0.0, total - st.session_state[f"ot_bank_val_{d}"])
    return callback

def make_update_banco(d, total):
    def callback():
        st.session_state[f"ot_bank_val_{d}"] = max(0.0, total - st.session_state[f"ot_pay_val_{d}"])
    return callback

# 3. Captura del usuario desde la URL
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
    if st.session_state.get(f"reset_requested_{dia}", False):
        st.session_state[f"lineas_{dia}"] = [{
            "in": "", "out": "", "abs": "-", 
            "serv": "Service (WO)", "ord": "", 
            "loc": "Candiac (Z8)", "comm": ""
        }]
        st.session_state[f"ot_bank_val_{dia}"] = 0.0
        st.session_state[f"ot_pay_val_{dia}"] = 0.0
        st.session_state[f"reset_requested_{dia}"] = False

    if f"lineas_{dia}" not in st.session_state:
        st.session_state[f"lineas_{dia}"] = [
            {"in": "", "out": "", "abs": "-", "serv": "Service (WO)", "ord": "352886", "loc": "Candiac (Z8)", "comm": ""}
        ]
    
    if f"ot_bank_val_{dia}" not in st.session_state:
        st.session_state[f"ot_bank_val_{dia}"] = 0.0
    if f"ot_pay_val_{dia}" not in st.session_state:
        st.session_state[f"ot_pay_val_{dia}"] = 0.0

# --- RENDERIZADO DE ACORDEONES POR DÍA ---
for dia in dias:
    esta_abierto = True if "Lundi" in dia else False
    
    lineas_actuales = st.session_state[f"lineas_{dia}"]
    
    # Calcular horas totales ingresadas y detectar OT dinámicamente
    total_horas_dia = 0.0
    for idx, linea in enumerate(lineas_actuales):
        in_val = st.session_state.get(f"in_{dia}_{idx}", linea["in"])
        out_val = st.session_state.get(f"out_{dia}_{idx}", linea["out"])
        try:
            h_in = float(in_val) if in_val != "" else 0.0
            h_out = float(out_val) if out_val != "" else 0.0
            if h_out > h_in:
                total_horas_dia += (h_out - h_in)
        except ValueError:
            pass

    # Lógica de horas regulares (ej. 7.5h) vs Overtime
    rt_disponible = min(total_horas_dia, 7.5)
    ot_disponible = max(0.0, total_horas_dia - 7.5)

    num_lineas = len(lineas_actuales)
    label_acordeon = f"{dia}  •  {total_horas_dia:.2f}h Total ({num_lineas} lignes)"

    with st.expander(label_acordeon, expanded=esta_abierto):
        
        for idx, linea in enumerate(lineas_actuales):
            cols = st.columns([1, 1, 1.4, 1.8, 1.8, 1.8, 2, 0.8])
            
            with cols[0]:
                st.text_input("In", value=linea["in"], placeholder="8", key=f"in_{dia}_{idx}")
            with cols[1]:
                st.text_input("Out", value=linea["out"], placeholder="16", key=f"out_{dia}_{idx}")
            with cols[2]:
                st.selectbox("Abs", ["-", "Maladie", "Vacances"], index=0, key=f"abs_{dia}_{idx}")
            with cols[3]:
                st.selectbox("Service", ["Service (WO)", "Interne (WO)", "PM"], index=0, key=f"serv_{dia}_{idx}")
            with cols[4]:
                st.text_input("Order Ref", value=linea["ord"], key=f"ord_{dia}_{idx}")
            with cols[5]:
                st.selectbox("Loc", ["Candiac (Z8)", "Mirabel", "Saint-Jérôme", "Autre"], index=0, key=f"loc_{dia}_{idx}")
            with cols[6]:
                st.text_input("Comm", value=linea["comm"], placeholder="Opt", key=f"com_{dia}_{idx}")
            with cols[7]:
                st.markdown("<br>", unsafe_allow_html=True)
                btn_del_key = f"del_line_{dia}_{idx}"
                if st.button("🗑️", key=btn_del_key, help="Supprimer cette ligne"):
                    for i in range(len(st.session_state[f"lineas_{dia}"])):
                        st.session_state[f"lineas_{dia}"][i]["in"] = st.session_state.get(f"in_{dia}_{i}", st.session_state[f"lineas_{dia}"][i]["in"])
                        st.session_state[f"lineas_{dia}"][i]["out"] = st.session_state.get(f"out_{dia}_{i}", st.session_state[f"lineas_{dia}"][i]["out"])
                    
                    if len(st.session_state[f"lineas_{dia}"]) > 1:
                        st.session_state[f"lineas_{dia}"].pop(idx)
                        st.rerun()
                    else:
                        st.warning("Min 1")

        # Mostrar sección de Overtime SOLO si se superan las horas normales (> 7.5h)
        if ot_disponible > 0:
            st.markdown(
                f"**À confirmer →** <span class='ot-badge'>OT {ot_disponible:.2f}h</span> + <span class='rt-badge'>RT {rt_disponible:.2f}h</span>", 
                unsafe_allow_html=True
            )

            aviso_ot = f"⚠️ Shift hors heures standard ({ot_disponible:.2f}h au-delà de 7.5h)"
            st.markdown(f"""
<div style="background-color: #1F2937; border: 1px solid #374151; padding: 10px; border-radius: 8px; color: #F3F4F6; margin-top: 8px; margin-bottom: 8px;">
    <strong>{aviso_ot}</strong><br>
    <small>👉 Répartition des heures d'Overtime disponibles ({ot_disponible:.2f}h max) :</small>
</div>
""", unsafe_allow_html=True)
            
            key_banco = f"ot_bank_val_{dia}"
            key_pago = f"ot_pay_val_{dia}"
            
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                st.number_input(
                    "🏛️ OT en banque", min_value=0.0, max_value=ot_disponible, step=0.5, 
                    key=key_banco, on_change=make_update_pago(dia, ot_disponible)
                )
            with col_sel2:
                st.number_input(
                    "💰 OT à payer", min_value=0.0, max_value=ot_disponible, step=0.5, 
                    key=key_pago, on_change=make_update_banco(dia, ot_disponible)
                )
        else:
            st.markdown(
                f"**À confirmer →** <span class='rt-badge'>RT {rt_disponible:.2f}h</span>", 
                unsafe_allow_html=True
            )

        # Botones inferiores del día
        st.write("")
        c_add, c_nuit, c_reset = st.columns([3, 3, 2])
        
        with c_add:
            if st.button("➕ Ajouter une ligne", key=f"add_btn_{dia}", use_container_width=True):
                for i in range(len(st.session_state[f"lineas_{dia}"])):
                    st.session_state[f"lineas_{dia}"][i]["in"] = st.session_state.get(f"in_{dia}_{i}", st.session_state[f"lineas_{dia}"][i]["in"])
                    st.session_state[f"lineas_{dia}"][i]["out"] = st.session_state.get(f"out_{dia}_{i}", st.session_state[f"lineas_{dia}"][i]["out"])
                
                ultimo_out = st.session_state[f"lineas_{dia}"][-1]["out"] or "16"
                
                st.session_state[f"lineas_{dia}"].append({
                    "in": ultimo_out, 
                    "out": "", 
                    "abs": "-", 
                    "serv": "Service (WO)", 
                    "ord": "", 
                    "loc": "Candiac (Z8)", 
                    "comm": ""
                })
                st.rerun()

        with c_nuit:
            st.button("🌙 Nuit à l'extérieur", key=f"nuit_{dia}", use_container_width=True)
            
        with c_reset:
            if st.button("Réinitialiser", key=f"reset_btn_{dia}", use_container_width=True):
                st.session_state[f"reset_requested_{dia}"] = True
                st.rerun()
