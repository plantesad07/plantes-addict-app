import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Plantes Addict - Coach Main Verte", layout="centered")

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #e2001a !important; text-align: center; }
    div[data-testid="stExpander"] { border: 2px solid #e2001a; border-radius: 15px; }
    .stButton>button { 
        background-color: #e2001a !important; 
        color: white !important; 
        border-radius: 30px !important; 
        width: 100%; height: 50px; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png")
st.title("Votre Coach Main Verte 🌿")

# --- CHARGEMENT DONNÉES ---
@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv("plantes.csv")

@st.cache_data(ttl=60)
def load_villes():
    df_v = pd.read_csv("config.csv")
    return df_v['ville'].unique().tolist()

df = load_data()
villes_list = load_villes()

if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRAN 1 : ACCUEIL ---
if st.session_state.etape == 'accueil':
    st.write("### 🏠 Bienvenue !")
    email = st.text_input("Votre email :")
    ville = st.selectbox("Ville :", villes_list)
    
    if st.button("Lancer mon diagnostic"):
        if email and "@" in email:
            # ENREGISTREMENT DANS GOOGLE SHEETS
            try:
                # On lit les données actuelles
                existing_data = conn.read(worksheet="Feuille 1")
                # On prépare la nouvelle ligne
                new_entry = pd.DataFrame([{"Email": email, "Ville": ville, "Date": pd.Timestamp.now()}] )
                # On fusionne et on met à jour
                updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
                conn.update(worksheet="Feuille 1", data=updated_data)
            except:
                pass # Évite de bloquer l'utilisateur si la connexion Sheets échoue
            
            st.session_state.email = email
            st.session_state.ville = ville
            st.session_state.etape = 'diagnostic'
            st.rerun()

# --- ÉCRAN 2 : DIAGNOSTIC ---
elif st.session_state.etape == 'diagnostic':
    st.write(f"📍 Boutique : **{st.session_state.ville}**")
    lieu = st.radio("Emplacement :", ["Intérieur", "Extérieur"])
    
    col_a, col_b = st.columns(2)
    with col_a:
        depolluante = st.toggle("🍃 Dépolluante")
        animaux = st.toggle("🐱 Animaux Safe")
    with col_b:
        salle_de_bain = st.toggle("🚿 Salle de bain")
        expo = st.radio("Lumière :", ["Ombre", "Vive", "Directe"])

    # FILTRAGE
    recos = df[df['lieu'] == lieu]
    if depolluante: recos = recos[recos['depolluante'] == "Oui"]
    if salle_de_bain: recos = recos[recos['salle_de_bain'] == "Oui"]
    if animaux: recos = recos[recos['animaux_safe'] == "Oui"]
    recos = recos[recos['lumiere'] == expo]

    st.markdown("---")
    if recos.empty:
        st.info("Aucune plante ne correspond pile à ces critères. Demandez à nos experts !")
    else:
        for _, row in recos.iterrows():
            with st.container(border=True):
                st.subheader(row['nom'])
                st.write(f"🚿 **Entretien :** {row['entretien']}")
                st.info(f"💡 {row['conseil']}")

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
