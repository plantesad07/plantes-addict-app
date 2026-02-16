import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Plantes Addict - Coach Main Verte", layout="centered")

# --- DESIGN PERSONNALISÉ (ROUGE PLANTES ADDICT) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #e2001a !important; text-align: center; }
    div[data-testid="stExpander"] { border: 2px solid #e2001a; border-radius: 15px; }
    .stButton>button { 
        background-color: #e2001a !important; 
        color: white !important; 
        border-radius: 30px !important; 
        width: 100%;
        height: 50px;
        font-weight: bold !important;
    }
    .badge-froid {
        background-color: #007bff;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO CENTRÉ ---
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
with col_logo_2:
    # On force l'affichage du logo via ton URL officielle
    st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", use_container_width=True)

st.title("Votre Coach Main Verte Personnel 🌿")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv("plantes.csv")

@st.cache_data(ttl=60)
def load_villes():
    df_v = pd.read_csv("config.csv")
    return df_v['ville'].unique().tolist()

try:
    df = load_data()
    villes_list = load_villes()
except Exception as e:
    st.error(f"Erreur fichiers : {e}")
    st.stop()

if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRAN 1 : ACCUEIL ---
if st.session_state.etape == 'accueil':
    st.write("### 🏠 Bienvenue à la vente !")
    email = st.text_input("Votre email :", placeholder="exemple@email.com")
    ville = st.selectbox("Choisissez votre ville :", villes_list)
    
    if st.button("Lancer mon diagnostic"):
        if email and "@" in email:
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
    lieu = st.radio("Emplacement :", ["Intérieur", "Extérieur"])
    
    st.subheader("Vos besoins spécifiques :")
    col_a, col_b = st.columns(2)
    with col_a:
        depolluante = st.toggle("🍃 Plante dépolluante")
        animaux = st.toggle("🐱 J'ai des animaux")
    with col_b:
        salle_de_bain = st.toggle("🚿 Pour ma salle de bain")
        expo = st.radio("Lumière :", ["Ombre", "Vive", "Directe"])

    # FILTRAGE
    recos = df.copy()
    if 'lieu' in recos.columns:
        recos = recos[recos['lieu'] == lieu]
    if depolluante and 'depolluante' in recos.columns:
        recos = recos[recos['depolluante'] == "Oui"]
    if salle_de_bain and 'salle_de_bain' in recos.columns:
        recos = recos[recos['salle_de_bain'] == "Oui"]
    if animaux and 'animaux_safe' in recos.columns:
        recos = recos[recos['animaux_safe'] == "Oui"]
    if expo and 'lumiere' in recos.columns:
        recos = recos[recos['lumiere'] == expo]

    st.markdown("---")
    st.subheader(f"✨ Notre sélection pour vous :")
    
    if recos.empty:
        st.info("Aucune plante ne correspond exactement à vos critères. Demandez à nos experts !")
    else:
        for _, row in recos.iterrows():
            with st.container(border=True):
                # Affichage du badge froid pour l'extérieur
                if lieu == "Extérieur" and 'resistance' in row and pd.notna(row['resistance']):
                    st.markdown(f"❄️ **Résistance : {row['resistance']}**")
                
                st.subheader(row['nom'])
                st.write(f"🚿 **Entretien :** {row['entretien']}")
                st.info(f"💡 {row['conseil']}")

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
