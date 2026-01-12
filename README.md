# MoroTwin : Jumeau Numérique & IA pour la Supply Chain (Maroc)

**MoroTwin** est une plateforme de "Control Tower" intelligente basée sur le concept de **Digital Twin** (Jumeau Numérique). Elle permet de simuler, surveiller et optimiser les flux logistiques sur le réseau routier marocain en utilisant l'Intelligence Artificielle pour la résolution automatique d'incidents (**Self-Healing**).

!

---

##  Problématique & Solution
Dans un environnement logistique complexe, les imprévus (trafic, météo, pannes) coûtent cher. MoroTwin répond à ce défi en :
1. **Simulant** une flotte de camions en temps réel.
2. **Détectant** les anomalies avant qu'elles ne deviennent critiques.
3. **Automatisant** la prise de décision (choix entre Re-routage, Envoi Express ou Attente) pour maximiser le **ROI**.

---

##  Fonctionnalités Clés

### 1. Cartographie Dynamique (Folium)
- Visualisation interactive de la flotte sur les axes routiers majeurs (Casa, Tanger, Agadir, Marrakech).
- **Zoom Intelligent** : La carte se focalise automatiquement sur le camion sélectionné pour une analyse précise.
- Tracé des itinéraires (PolyLines) avec codes couleurs selon le statut (OK / Incident).

### 2.Moteur de Décision (Self-Healing AI)
- Analyse multicritères basée sur des poids configurables (Coût, Risque SLA, Fiabilité).
- Calcul instantané de l'arbitrage financier : *Coût de la solution vs Pénalités de retard*.

### 3.Business Intelligence (Plotly)
- Dashboard ROI interactif montrant les gains réalisés grâce aux interventions de l'IA.
- Graphiques Sunburst pour analyser la performance par type de marchandise (Périssable, Standard, etc.).



---

## Stack Technique
- **Backend/Logic :** Python 3.x
- **Interface :** Streamlit
- **Visualisation Géo :** Folium & Streamlit-Folium
- **Data Analytics :** Pandas, Plotly, NumPy

---

## Installation & Utilisation

1. **Cloner le projet :**
   ```bash
   git clone [https://git@github.com:Ousshadd/MoroTwin.git
   cd MoroTwin
   Create a virtual environment:
	python -m venv venv
	source venv/bin/activate  # On Windows: venv\Scripts\activate
   	pip install -r requirements.txt	
   	streamlit run main_app.py
