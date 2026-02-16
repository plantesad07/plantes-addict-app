import streamlit as st
import pandas as pd

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Plantes Addict - Guide Local", layout="centered")

# Chargement des villes de la semaine
@st.cache_data
def get_villes():
    try:
        # Lit le fichier config.csv que vous modifiez chaque semaine
        villes_df = pd.read_csv("config.csv")
        return villes_df['ville'].tolist()
    except:
        return ["Vente en cours"] # Valeur par défaut si fichier manquant

villes_actives = get_villes()

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f1; }
    .main-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        text-align: center;
    }
    .stSelectbox label { font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE D'AUTHENTIFICATION ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- PAGE DE CONNEXION ---
if not st.session_state.auth:
    st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", width=200)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🌿 Bienvenue chez Plantes Addict")
        st.write("Sélectionnez votre ville pour accéder au catalogue de la semaine et aux conseils d'entretien.")
        
        email = st.text_input("Votre adresse email")
        
        # ICI : La liste se met à jour selon votre fichier config.csv
        ville_choisie = st.selectbox("Où nous trouvez-vous aujourd'hui ?", villes_actives)
        
        if st.button("Accéder au guide"):
            if email and "@" in email:
                # Sauvegarde des infos (On peut lier ici à Google Sheets)
                st.session_state.auth = True
                st.session_state.ville = ville_choisie
                st.session_state.email = email
                st.rerun()
            else:
                st.error("Merci d'entrer un email valide pour continuer.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE CATALOGUE (Une fois connecté) ---
else:
    st.title(f"Jungle à {st.session_state.ville} 📍")
    st.write(f"Bonjour ! Voici les conseils pour vos plantes achetées ce week-end.")
    
    # Bouton de recherche
    search = st.text_input("🔍 Rechercher une plante (ex: Alocasia, Monstera...)")
    
    # Affichage des plantes (chargé depuis plantes.csv)
    df = pd.read_csv("plantes.csv")
    
    if search:
        df = df[df['nom'].str.contains(search, case=False)]
    
    for i, row in df.iterrows():
        with st.expander(f"🌿 {row['nom']}"):
            st.write(f"**Niveau :** {row['entretien']} | **Lumière :** {row['lumiere']}")
            st.info(f"**Conseil d'expert :** {row['conseil']}")

    if st.button("Quitter le guide"):
        st.session_state.auth = False
        st.rerun()
