import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Plantes Addict - Coach", layout="centered")

# --- DESIGN MOBILE-FIRST ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #e2001a !important; text-align: center; }
    /* Style des cartes de plantes */
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        border: 2px solid #e2001a !important; 
        border-radius: 15px !important; 
        padding: 20px !important;
        background-color: #fffafa !important;
        margin-bottom: 10px !important;
    }
    /* Style du bouton Recommencer */
    .stButton>button { 
        background-color: #e2001a !important; 
        color: white !important; 
        border-radius: 50px !important; 
        width: 100%; height: 50px; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO CENTRÉ (Fix Affichage) ---
st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", use_container_width=True)
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

df = load_data()
villes_list = load_villes()

if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRAN 1 : ACCUEIL ---
if st.session_state.etape == 'accueil':
    st.write("### Bienvenue !")
    email = st.text_input("Votre email :")
    ville = st.selectbox("Ville :", villes_list)
    
    if st.button("Lancer mon diagnostic ✨"):
        if email and "@" in email:
            if conn:
                try:
                    # On utilise EXACTEMENT tes titres : Email, Ville, DATE
                    data = conn.read(worksheet="Feuille 1")
                    new_row = pd.DataFrame([{
                        "Email": email, 
                        "Ville": ville, 
                        "DATE": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                    }])
                    updated_df = pd.concat([data, new_row], ignore_index=True)
                    conn.update(worksheet="Feuille 1", data=updated_df)
                except Exception as e:
                    st.error(f"Erreur technique Sheets : {e}")
            
            st.session_state.email = email
            st.session_state.ville = ville
            st.session_state.etape = 'diagnostic'
            st.rerun()

# --- ÉCRAN 2 : DIAGNOSTIC ---
elif st.session_state.etape == 'diagnostic':
    st.write(f"📍 Boutique : **{st.session_state.ville}**")
    lieu = st.radio("Où sera la plante ?", ["Intérieur", "Extérieur"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        depolluante = st.toggle("🍃 Dépolluante")
        animaux = st.toggle("🐱 Animaux Safe")
    with col2:
        salle_de_bain = st.toggle("🚿 Salle de bain")
        
    expo = st.select_slider("Lumière :", options=["Ombre", "Vive", "Directe"])

    # FILTRAGE
    recos = df[df['lieu'] == lieu].copy()
    if depolluante: recos = recos[recos['depolluante'] == "Oui"]
    if salle_de_bain: recos = recos[recos['salle_de_bain'] == "Oui"]
    if animaux: recos = recos[recos['animaux_safe'] == "Oui"]
    recos = recos[recos['lumiere'] == expo]

    st.write("---")
    if recos.empty:
        st.info("Aucune plante ne correspond exactement.")
    else:
        for _, row in recos.iterrows():
            with st.container(border=True):
                # Affichage des degrés pour l'extérieur
                if lieu == "Extérieur" and 'resistance' in row:
                    st.markdown(f"❄️ **Résistance : {row['resistance']}**")
                st.subheader(row['nom'])
                st.write(f"🚿 **Entretien :** {row['entretien']}")
                st.info(f"💡 {row['conseil']}")

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
