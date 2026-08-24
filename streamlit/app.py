import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from pathlib import Path

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="DataInsight Solutions - Application Sécurisée", layout="wide")

# ==========================================
# 1. INITIALISATION DE LA SESSION
# ==========================================
# st.session_state permet de garder en mémoire l'état de connexion de l'utilisateur
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = ""

# ==========================================
# 2. FONCTIONS DE CHARGEMENT ET D'AUTHENTIFICATION
# ==========================================
@st.cache_data
def load_accounts():
    """Lit le fichier accounts.csv situé dans le même dossier que app.py"""
    BASE_DIR = Path(__file__).resolve().parent
    accounts_path = BASE_DIR / "accounts.csv"
    return pd.read_csv(accounts_path)

def authenticate(username_input, password_input):
    """Vérifie si le couple (nom, mot de passe) existe dans le CSV"""
    try:
        accounts_df = load_accounts()
        # Suppression des espaces superflus dans les chaînes
        accounts_df['name'] = accounts_df['name'].astype(str).str.strip()
        accounts_df['password'] = accounts_df['password'].astype(str).str.strip()
        
        user_match = accounts_df[
            (accounts_df["name"] == username_input.strip()) & 
            (accounts_df["password"] == password_input.strip())
        ]
        return not user_match.empty
    except Exception as e:
        st.error(f"Erreur de lecture du fichier accounts.csv : {e}")
        return False

@st.cache_data
def load_taxis_data():
    """Charge les données des taxis"""
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/taxis.csv"
    df = pd.read_csv(url)
    df['pickup'] = pd.to_datetime(df['pickup'])
    return df

# ==========================================
# 3. GESTION DE L'AFFICHAGE CONDITIONNEL
# ==========================================

# --- CAS 1 : UTILISATEUR NON CONNECTÉ ---
if not st.session_state["logged_in"]:
    st.title("🔒 Connexion à l'Application DataInsight")
    st.subheader("Veuillez vous identifier pour accéder au contenu")
    
    col_login, _ = st.columns([1, 1])
    with col_login:
        username_input = st.text_input("Nom d'utilisateur")
        password_input = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            if authenticate(username_input, password_input):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username_input
                st.success(f"Bienvenue {username_input} !")
                st.rerun() # Relance le script pour afficher l'application sécurisée
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

# --- CAS 2 : UTILISATEUR CONNECTÉ ---
else:
    # --- BARRE LATÉRALE (SIDEBAR) ---
    with st.sidebar:
        st.write(f"👤 Connecté en tant que : **{st.session_state['username']}**")
        if st.button("Se déconnecter"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun() # Relance le script pour afficher la page de connexion
        
        st.divider()
        
        # Menu de navigation avec streamlit-option-menu
        selected_page = option_menu(
            menu_title="Navigation",
            options=["Dashboard Taxis", "Galerie Photos"],
            icons=["bar-chart-fill", "images"],
            default_index=0
        )

    # --- PAGE 1 : DASHBOARD TAXIS ---
    if selected_page == "Dashboard Taxis":
        st.title("🚖 Dashboard d'Analyse des Taxis")
        st.write("Bienvenue sur la plateforme sécurisée de DataInsight Solutions.")
        
        df = load_taxis_data()

        # Filtres
        st.header("Filtres")
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            quartiers = ["Tous"] + list(df['pickup_borough'].dropna().unique())
            quartier_choisi = st.selectbox("Sélectionnez le quartier de départ :", options=quartiers)
            
        with col_f2:
            paiement_options = ["Tous"] + list(df['payment'].dropna().unique())
            paiement_choisi = st.radio("Mode de paiement :", options=paiement_options, horizontal=True)

        # Application des filtres
        df_filtre = df.copy()
        if quartier_choisi != "Tous":
            df_filtre = df_filtre[df_filtre['pickup_borough'] == quartier_choisi]
        if paiement_choisi != "Tous":
            df_filtre = df_filtre[df_filtre['payment'] == paiement_choisi]

        # KPIs
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        total_courses = len(df_filtre)
        prix_moyen = df_filtre['total'].mean() if total_courses > 0 else 0
        distance_moyenne = df_filtre['distance'].mean() if total_courses > 0 else 0

        with col_kpi1:
            st.metric("Nombre total de courses", value=f"{total_courses:,}")
        with col_kpi2:
            st.metric("Prix moyen ($)", value=f"{prix_moyen:.2f} $")
        with col_kpi3:
            st.metric("Distance moyenne (miles)", value=f"{distance_moyenne:.2f}")

        # Graphiques
        st.divider()
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Distance vs Prix total")
            if not df_filtre.empty:
                fig_scatter = px.scatter(
                    df_filtre, x="distance", y="total", color="payment",
                    title="Distance (miles) vs Prix Total ($)"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible.")
                
        with col_g2:
            st.subheader("Répartition des passagers")
            if not df_filtre.empty:
                st.bar_chart(df_filtre['passengers'].value_counts())
            else:
                st.warning("Aucune donnée disponible.")

    # --- PAGE 2 : GALERIE PHOTOS ---
    elif selected_page == "Galerie Photos":
        st.title("🖼️ Galerie d'Images (Mascottes)")
        st.write("Affichage d'images alignées sur 3 colonnes côte à côte.")

        sample_images = [
            "https://static.streamlit.io/examples/cat.jpg",
            "https://static.streamlit.io/examples/dog.jpg",
            "https://static.streamlit.io/examples/owl.jpg"
        ]

        # Disposition sur 3 colonnes (st.columns(3))
        cols = st.columns(3)
        for idx, img_url in enumerate(sample_images):
            with cols[idx % 3]:
                st.image(img_url, caption=f"Mascotte {idx + 1}", use_container_width=True)