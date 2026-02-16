import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Plantes Addict - Coach Main Verte", 
    layout="centered"
)

# --- DESIGN PERSONNALISÉ (ROUGE PLANTES ADDICT) ---
st.markdown("""
    <style>
    :root { --rouge-pa: #e2001a; }
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: var(--rouge-pa) !important; text-align: center; }
    
    .reco-card { 
        border: 2px solid var(--rouge-pa); 
        background: #fffafa; 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 20px;
    }
    
    .stButton>button { 
        background-color: var(--rouge-pa) !important; 
        color: white !important; 
        border-radius: 30px !important; 
        padding: 12px 30px !important;
        width: 100%;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    return pd.read_csv("plantes.csv")

@st.cache_data
def load_villes():
    return pd.read_csv("config.csv")['ville'].tolist()

df = load_data()
villes = load_villes()

# --- AFFICHAGE DU LOGO ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=250)
else:
    st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", width=250)

st.title("Votre Coach Main Verte Personnel 🌿")

# --- SYSTÈME D'ÉTAPE ---
if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRAN 1 : ACCUEIL ---
if st.session_state.etape == 'accueil':
    st.write("### 🏠 Bienvenue à la vente !")
    email = st.text_input("Votre email :")
    ville = st.selectbox("Ville actuelle :", villes)
    
    if st.button("Lancer mon diagnostic"):
        if email and "@" in email:
            st.session_state.email = email
            st.session_state.ville = ville
            st.session_state.etape = 'diagnostic'
            st.rerun()
        else:
            st.warning("Veuillez entrer un email valide.")

# --- ÉCRAN 2 : LE DIAGNOSTIC ---
elif st.session_state.etape == 'diagnostic':
    st.subheader("Quel est votre environnement ?")
    
    col1, col2 = st.columns(2)
    with col1:
        expo = st.radio("Lumière :", ["Ombre", "Vive", "Directe"])
        taille = st.multiselect("Format :", ["Petite", "Moyenne", "Grande"])
    with col2:
        niveau = st.select_slider("Niveau :", options=["Débutant", "Habitué", "Expert"])
        animaux = st.toggle("🐱 J'ai des animaux")

    # Filtrage (sans prix)
    recos = df.copy()
    if animaux:
        recos = recos[recos['animaux_safe'] == "Oui"]
    if expo:
        recos = recos[recos['lumiere'] == expo]
    if taille:
        recos = recos[recos['categorie'].isin(taille)]

    st.markdown("---")
    st.subheader("✨ Nos recommandations :")

    if recos.empty:
        st.info("Demandez conseil à nos experts sur place !")
    else:
        for _, row in recos.head(3).iterrows():
            st.markdown(f"""
                <div class="reco-card">
                    <h3 style="margin:0; text-align:left;">{row['nom']}</h3>
                    <p style="font-size: 14px; margin-top: 10px;">🚿 <b>Entretien :</b> {row['entretien']}</p>
                    <p style="font-size: 14px; background: #fff; padding: 10px; border-radius: 5px;">💡 <b>Conseil :</b> {row['conseil']}</p>
                </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()

st.markdown("<br><hr><center><p style='color: #999; font-size: 12px;'>© Plantes Addict</p></center>", unsafe_allow_html=True)
