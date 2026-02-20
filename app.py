import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Plantes Addict - Coach", layout="centered")

# --- DESIGN MOBILE-FIRST (ROUGE PLANTES ADDICT) ---
st.markdown("""
    <style>
    /* Global */
    .stApp { background-color: #ffffff; }
    
    /* Titres */
    h1 { color: #e2001a !important; font-size: 1.8rem !important; text-align: center; margin-bottom: 0px; }
    h2, h3 { color: #e2001a !important; font-size: 1.2rem !important; }
    
    /* Cartes Plantes - Optimisé Mobile */
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        border: 1px solid #e2001a !important; 
        border-radius: 12px !important; 
        padding: 15px !important;
        background-color: #fffafa !important;
        margin-bottom: 10px !important;
    }

    /* Boutons */
    .stButton>button { 
        background-color: #e2001a !important; 
        color: white !important; 
        border-radius: 50px !important; 
        width: 100%; height: 55px; 
        font-weight: bold !important;
        font-size: 1.1rem !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox {
        border-radius: 10px !important;
    }

    /* Badge Froid */
    .froid-label {
        background-color: #007bff;
        color: white;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO (URL DIRECTE + TAILLE MOBILE) ---
# On utilise du HTML simple pour être sûr que le logo s'affiche et soit centré
st.markdown("<div style='text-align: center;'><img src='https://www.plantesaddict.fr/img/logo-plantes-addict.png' width='180'></div>", unsafe_allow_html=True)

st.title("Mon Coach Main Verte 🌿")

# --- CONNEXION GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv("plantes.csv")

@st.cache_data(ttl=60)
def load_villes():
    return pd.read_csv("config.csv")['ville'].unique().tolist()

try:
    df = load_data()
    villes_list = load_villes()
except:
    st.error("⚠️ Fichiers de données introuvables sur GitHub.")
    st.stop()

if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRAN 1 : ACCUEIL ---
if st.session_state.etape == 'accueil':
    st.write("---")
    st.write("### Trouver la plante parfaite en 1 minute !")
    
    email = st.text_input("Votre email (pour vos conseils) :", placeholder="votre@email.com")
    ville = st.selectbox("Ville de la vente :", villes_list)
    
    if st.button("Lancer mon diagnostic ✨"):
        if email and "@" in email:
            # Enregistrement dans Google Sheets
            if conn:
                try:
                    # Lecture de l'onglet "Feuille 1"
                    existing_data = conn.read(worksheet="Feuille 1")
                    new_entry = pd.DataFrame([{
                        "Email": email, 
                        "Ville": ville, 
                        "Date": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                    }])
                    updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
                    conn.update(worksheet="Feuille 1", data=updated_data)
                except Exception as e:
                    # On ne bloque pas l'utilisateur si Sheets échoue, mais on peut debugger ici
                    pass
            
            st.session_state.email = email
            st.session_state.ville = ville
            st.session_state.etape = 'diagnostic'
            st.rerun()
        else:
            st.error("❌ Merci d'entrer un email valide pour continuer.")

# --- ÉCRAN 2 : DIAGNOSTIC ---
elif st.session_state.etape == 'diagnostic':
    st.write(f"📍 Vente : **{st.session_state.ville}**")
    
    st.write("### Vos critères :")
    lieu = st.radio("Où sera la plante ?", ["Intérieur", "Extérieur"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        depolluante = st.toggle("🍃 Dépolluante")
        animaux = st.toggle("🐱 Animaux Safe")
    with col2:
        salle_de_bain = st.toggle("🚿 Salle de bain")
        
    expo = st.select_slider("Lumière disponible :", options=["Ombre", "Vive", "Directe"])

    # FILTRAGE
    recos = df[df['lieu'] == lieu].copy()
    if depolluante: recos = recos[recos['depolluante'] == "Oui"]
    if salle_de_bain: recos = recos[recos['salle_de_bain'] == "Oui"]
    if animaux: recos = recos[recos['animaux_safe'] == "Oui"]
    recos = recos[recos['lumiere'] == expo]

    st.write("---")
    st.write(f"### ✨ Notre sélection pour vous :")
    
    if recos.empty:
        st.warning("Aucune plante ne correspond à 100% à ce mélange. Demandez conseil à l'équipe sur place !")
    else:
        for _, row in recos.iterrows():
            with st.container(border=True):
                # Badge froid pour l'extérieur
                if lieu == "Extérieur" and 'resistance' in row and pd.notna(row['resistance']):
                    st.markdown(f"<span class='froid-label'>❄️ Résiste à {row['resistance']}</span>", unsafe_allow_html=True)
                
                st.subheader(row['nom'])
                st.write(f"🚿 **Entretien :** {row['entretien']}")
                st.info(f"💡 {row['conseil']}")

    if st.button("🔄 Recommencer le test"):
        st.session_state.etape = 'accueil'
        st.rerun()
