import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Plantes Addict - Coach Main Verte", layout="centered")

# --- DESIGN ROUGE PLANTES ADDICT ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #e2001a !important; text-align: center; font-family: sans-serif; }
    /* Style des cartes de plantes */
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        border: 2px solid #e2001a !important; 
        border-radius: 15px !important; 
        padding: 20px !important;
        background-color: #fffafa !important;
    }
    .stButton>button { 
        background-color: #e2001a !important; 
        color: white !important; 
        border-radius: 30px !important; 
        width: 100%; height: 50px; font-weight: bold !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO CENTRÉ (Correction affichage) ---
st.markdown("<center><img src='https://www.plantesaddict.fr/img/logo-plantes-addict.png' width='250'></center>", unsafe_allow_html=True)
st.title("Votre Coach Main Verte 🌿")

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
except Exception as e:
    st.error("Erreur de lecture des fichiers CSV. Vérifiez plantes.csv et config.csv.")
    st.stop()

if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRAN 1 : ACCUEIL ---
if st.session_state.etape == 'accueil':
    st.write("### 🏠 Bienvenue à la vente !")
    email = st.text_input("Votre email pour recevoir nos conseils :", placeholder="exemple@email.com")
    ville = st.selectbox("Choisissez votre ville :", villes_list)
    
    if st.button("Lancer mon diagnostic"):
        if email and "@" in email:
            # Enregistrement dans Google Sheets
            if conn:
                try:
                    existing_data = conn.read(worksheet="Feuille 1")
                    new_entry = pd.DataFrame([{"Email": email, "Ville": ville, "Date": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")}])
                    updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
                    conn.update(worksheet="Feuille 1", data=updated_data)
                except:
                    pass # Continue même si Sheets est indisponible
            
            st.session_state.email = email
            st.session_state.ville = ville
            st.session_state.etape = 'diagnostic'
            st.rerun()
        else:
            st.warning("Veuillez entrer une adresse email valide.")

# --- ÉCRAN 2 : DIAGNOSTIC ---
elif st.session_state.etape == 'diagnostic':
    st.write(f"📍 Boutique : **{st.session_state.ville}**")
    
    st.subheader("Où souhaitez-vous placer vos plantes ?")
    lieu = st.radio("Emplacement :", ["Intérieur", "Extérieur"], horizontal=True)
    
    st.subheader("Vos besoins spécifiques :")
    col_a, col_b = st.columns(2)
    with col_a:
        depolluante = st.toggle("🍃 Dépolluante")
        animaux = st.toggle("🐱 Animaux Safe")
    with col_b:
        salle_de_bain = st.toggle("🚿 Salle de bain")
        expo = st.radio("Lumière :", ["Ombre", "Vive", "Directe"])

    # FILTRAGE
    recos = df[df['lieu'] == lieu].copy()
    if depolluante: recos = recos[recos['depolluante'] == "Oui"]
    if salle_de_bain: recos = recos[recos['salle_de_bain'] == "Oui"]
    if animaux: recos = recos[recos['animaux_safe'] == "Oui"]
    recos = recos[recos['lumiere'] == expo]

    st.markdown("---")
    st.subheader(f"✨ Notre sélection {lieu} :")
    
    if recos.empty:
        st.info("Aucune plante ne correspond exactement. Demandez conseil à nos experts sur place !")
    else:
        for _, row in recos.iterrows():
            with st.container(border=True):
                # Affichage de la résistance au froid pour l'extérieur
                if lieu == "Extérieur" and 'resistance' in row and pd.notna(row['resistance']):
                    st.markdown(f"<span style='color:#007bff; font-weight:bold;'>❄️ Résistance : {row['resistance']}</span>", unsafe_allow_html=True)
                
                st.subheader(row['nom'])
                st.write(f"🚿 **Entretien :** {row['entretien']}")
                st.info(f"💡 {row['conseil']}")

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
