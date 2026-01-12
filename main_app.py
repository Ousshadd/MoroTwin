import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import time
import plotly.express as px

# Import dyal les classes dyalek
from digitaltwin import TruckDigitalTwin
from decision_engine import get_best_resolution
from utils import safe_get

# -------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# -------------------------------------------------
st.set_page_config(
    page_title="Control Tower | Digital Twin Maroc",
    page_icon="🚛",
    layout="wide"
)

# Custom CSS bach n7iydo l-style dyal "AI Chat" u nrej3oh Dashboard pro
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 28px; color: #1E88E5; font-weight: bold; }
    .main-title { font-size: 32px; font-weight: bold; color: #262730; margin-bottom: 20px; border-left: 5px solid #1E88E5; padding-left: 15px; }
    .stButton>button { border-radius: 5px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 2. CHARGEMENT DES DONNÉES (CORRIGÉ)
# -------------------------------------------------
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"Fichier introuvable : {path}")
        return pd.DataFrame()

    # Nettoyage et Initialisation des colonnes (Fix AttributeError)
    if "sla_minutes" not in df.columns:
        df["sla_minutes"] = 180.0
    else:
        df["sla_minutes"] = df["sla_minutes"].fillna(180.0)
    
    df["sla_minutes"] = df["sla_minutes"].astype(float).clip(lower=30)

    if "eta_minutes" not in df.columns:
        if "dist_km" in df.columns:
            df["eta_minutes"] = df["dist_km"] / 70 * 60
        else:
            df["eta_minutes"] = 180.0
    else:
        df["eta_minutes"] = df["eta_minutes"].fillna(180.0).astype(float)

    defaults = {
        "status": "OK", "incident_type": "NONE", "load_type": "Standard",
        "origin": "Maroc", "destination": "Maroc", "penalty_mad": 2000.0,
        "reroute_cost_mad": 1200.0, "express_cost_mad": 2500.0
    }
    
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val
        else:
            df[col] = df[col].fillna(val)
            
    return df

df = load_data("data/maroc_supply_chain_pro.csv")

# -------------------------------------------------
# 3. GESTION DE L'ÉTAT (SESSION STATE)
# -------------------------------------------------
if "weights" not in st.session_state:
    st.session_state.weights = {"w_cost": 0.35, "w_sla": 0.45, "w_rel": 0.15}

def normalize_weights():
    s = sum(st.session_state.weights.values())
    if s > 0:
        for k in st.session_state.weights:
            st.session_state.weights[k] /= s

# -------------------------------------------------
# 4. SIDEBAR : PARAMÈTRES
# -------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠️ Centre de Contrôle")
    
    selected_id = st.selectbox(
        "Sélection du Camion",
        df["truck_id"].astype(str).unique() if not df.empty else ["N/A"],
        help="Identifiant unique du véhicule en transit"
    )
    
    st.divider()
    
    with st.expander("Scénarios 'What-if'", expanded=True):
        what_if = {
            "severe_weather": st.checkbox("Météo Défavorable", False),
            "traffic_peak": st.checkbox("Pic de Trafic (Heures de pointe)", True),
            "strike": st.checkbox("Blocage / Grèves", False),
        }
        fuel_increase = st.slider("Indexation Carburant (%)", 0, 50, 0)
        fuel_factor = 1 + fuel_increase / 100

    with st.expander("Pondérations de l'IA", expanded=False):
        w = st.session_state.weights
        w["w_cost"] = st.slider("Priorité Coût", 0.0, 1.0, w["w_cost"], 0.05)
        w["w_sla"] = st.slider("Priorité Respect SLA", 0.0, 1.0, w["w_sla"], 0.05)
        w["w_rel"] = st.slider("Priorité Fiabilité", 0.0, 1.0, w["w_rel"], 0.05)
        normalize_weights()

# -------------------------------------------------
# 5. MAIN DASHBOARD
# -------------------------------------------------
st.markdown('<p class="main-title">Digital Twin Control Tower • Logistics Morocco</p>', unsafe_allow_html=True)

if not df.empty:
    truck_info = df[df["truck_id"].astype(str) == str(selected_id)].iloc[0].to_dict()
    truck_info["reroute_cost_mad"] *= fuel_factor
    truck_info["express_cost_mad"] *= fuel_factor

    # Top KPI Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Status Système", "Opérationnel", delta="Online")
    m2.metric("Flotte Actuelle", f"{len(df)} Camions")
    m3.metric("Alertes Réseau", len(df[df["status"] != "OK"]), delta_color="inverse")
    m4.metric("Coût Carburant", f"+{fuel_increase}%", delta="-MAD")

    st.divider()

    # Simulation Section
    st.subheader("Analyse Prédictive : Jumeau Numérique")
    col_sim, col_info = st.columns([2, 1])

    with col_info:
        with st.container(border=True):
            st.markdown("**Fiche de Route**")
            st.write(f"**De:** {truck_info['origin']} ➡️ **Vers:** {truck_info['destination']}")
            st.write(f"**Chargement:** {truck_info['load_type']}")
            st.write(f"**ETA estimé:** {truck_info['eta_minutes']:.0f} min")
            risk_level = min(truck_info['eta_minutes']/truck_info['sla_minutes'], 1.0)
            st.progress(risk_level, text="Risque de retard (SLA)")

    with col_sim:
        if st.button("Lancer la Simulation de Trajet", type="primary", use_container_width=True):
            twin = TruckDigitalTwin(selected_id, truck_info, what_if)
            
            with st.status("Traitement des données télémétriques...", expanded=True) as status_prog:
                incident_at = None
                for p in range(0, 101, 20):
                    time.sleep(0.3)
                    status_curr = twin.predict_status(p)
                    
                    if status_curr == "INCIDENT_DETECTED":
                        incident_at = p
                        status_prog.update(label="Incident Critique Détecté !", state="error")
                        
                        st.error(f"Incident identifié à {p}% du parcours.")
                        action, new_eta, savings, explanation, score = get_best_resolution(
                            truck_info, st.session_state.weights
                        )
                        
                        with st.container(border=True):
                            st.markdown(f"### 🛡️ Recommandation : `{action}`")
                            st.write(f"**Gain estimé:** {savings:,.0f} MAD")
                            st.info(f"**Analyse IA:** {explanation}")
                        break
                
                if not incident_at:
                    status_prog.update(label="Simulation Terminée : Trajet Sécurisé", state="complete")
                    st.success("Le jumeau numérique ne prévoit aucune anomalie majeure.")

    # -------------------------------------------------
    # 6. BUSINESS INTELLIGENCE & MAP
    # -------------------------------------------------
    st.divider()
    st.subheader("Analyse de Performance Globale")

    # Calcul des résolutions pour toute la flotte
    res = df.apply(lambda r: pd.Series(get_best_resolution(r.to_dict(), st.session_state.weights)), axis=1)
    df_eval = df.copy()
    df_eval[["action", "new_eta_min", "savings", "explanation", "best_score"]] = res

    c1, c2, c3 = st.columns(3)
    c1.metric("Économies Totales", f"{df_eval['savings'].sum():,.0f} MAD")
    c2.metric("SLA Initial", f"{(df_eval['eta_minutes'] <= df_eval['sla_minutes']).mean()*100:.1f}%")
    c3.metric("SLA Après IA", f"{(df_eval['new_eta_min'] <= df_eval['sla_minutes']).mean()*100:.1f}%", delta="Optimisé")

    g1, g2 = st.columns(2)
    with g1:
        fig1 = px.bar(df_eval.groupby("action")["savings"].sum().reset_index(), 
                      x="action", y="savings", title="Impact Financier par Action",
                      color="action", template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)
    with g2:
        fig2 = px.pie(df_eval, names="incident_type", title="Répartition des Incidents Réseau",
                      hole=0.4, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

    # Map Section
    st.subheader("Géolocalisation Live")
    def generate_map(data, target_id):
        m = folium.Map(location=[31.7917, -7.0926], zoom_start=6, tiles="CartoDB positron")
        for _, row in data.head(30).iterrows():
            try:
                dest = list(map(float, str(row['dest_gps']).split(',')))
                is_selected = str(row['truck_id']) == str(target_id)
                folium.CircleMarker(
                    location=dest,
                    radius=10 if is_selected else 6,
                    color="#D32F2F" if row['status'] != "OK" else "#388E3C",
                    fill=True,
                    popup=f"Camion {row['truck_id']} - Action: {row['action']}"
                ).add_to(m)
            except: continue
        return m

    st_folium(generate_map(df_eval, selected_id), width=1400, height=500, key="map_global")

    # Export
    with st.expander("Détails des Opérations & Export CSV"):
        st.dataframe(df_eval[["truck_id", "origin", "destination", "action", "savings", "explanation"]].sort_values("savings", ascending=False), use_container_width=True)
        csv = df_eval.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger le rapport ROI", csv, "rapport_ia_logistique.csv", "text/csv")
else:
    st.warning("Veuillez vérifier que le fichier CSV est présent dans le dossier data/")