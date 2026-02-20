import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Plantes Addict - Coach", layout="centered")

# --- DESIGN MOBILE ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #e2001a !important; text-align: center; }
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        border: 2px solid #e2001a !important; border-radius: 15px !important; 
        padding: 20px !important; background-color: #fffafa !important; 
        margin-bottom: 10px !important;
    }
    .stButton>button { 
        background-color: #e2001a !important; color: white !important; 
        border-radius: 50px !important; width: 100%; height: 50px; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO (Correction : On utilise ton fichier logo.png local) ---
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
else:
    # Secours si le fichier n'est pas trouvé
    st.markdown("<h1 style='font-size: 40px;'>🌿 PLANTES ADDICT</h1>", unsafe_allow_html=True)

st.title("Mon Coach Main Verte")

# --- CONNEXION GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

# --- CHARGEMENT ---
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
    st.write("### Bienvenue à la vente !")
    email = st.text_input("Votre email :", placeholder="votre@email.com")
    ville = st.selectbox("Ville de la vente :", villes_list)
    
    if st.button("Lancer mon diagnostic ✨"):
        if email and "@" in email:
            if conn:
                try:
                    # On force la lecture de l'onglet "Feuille 1" (vu sur ton écran)
                    data = conn.read(worksheet="Feuille 1")
                    # On utilise EXACTEMENT tes titres : Email, Ville, DATE
                    new_row = pd.DataFrame([{
                        "Email": email, 
                        "Ville": ville, 
                        "DATE": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                    }])
                    updated_df = pd.concat([data, new_row], ignore_index=True)
                    conn.update(worksheet="Feuille 1", data=updated_df)
                    st.success("Email enregistré !")
                except Exception as e:
                    st.error(f"Erreur technique : {e}")
            
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
                st.subheader(row['nom'])
                st.write(f"🚿 **Entretien :** {row['entretien']}")
                st.info(f"💡 {row['conseil']}")

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
