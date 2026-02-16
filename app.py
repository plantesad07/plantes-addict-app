import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Plantes Addict - Coach Main Verte", layout="centered")

# --- DESIGN ROUGE ---
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
        box-shadow: 2px 4px 10px rgba(0,0,0,0.05);
    }
    .stButton>button { 
        background-color: var(--rouge-pa) !important; 
        color: white !important; 
        border-radius: 30px !important; 
        width: 100%;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO CENTRÉ ---
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
with col_logo_2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", use_container_width=True)

st.title("Votre Coach Main Verte Personnel 🌿")

# --- CHARGEMENT ---
@st.cache_data
def load_data():
    return pd.read_csv("plantes.csv")

@st.cache_data
def load_villes():
    return pd.read_csv("config.csv")['ville'].tolist()

df = load_data()
villes = load_villes()

if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ACCUEIL ---
if st.session_state.etape == 'accueil':
    st.write("### 🏠 Bienvenue !")
    email = st.text_input("Votre email :")
    ville = st.selectbox("Ville :", villes)
    if st.button("Lancer mon diagnostic"):
        if email and "@" in email:
            st.session_state.email = email
            st.session_state.ville = ville
            st.session_state.etape = 'diagnostic'
            st.rerun()

# --- DIAGNOSTIC ---
elif st.session_state.etape == 'diagnostic':
    st.write(f"📍 Vente : **{st.session_state.ville}**")
    
    st.subheader("Où souhaitez-vous placer vos plantes ?")
    lieu = st.radio("Type d'emplacement :", ["Intérieur", "Extérieur"])
    
    st.subheader("Détails de votre environnement :")
    c1, c2 = st.columns(2)
    with c1:
        expo = st.radio("Lumière :", ["Ombre", "Vive", "Directe"])
    with c2:
        animaux = st.toggle("🐱 J'ai des animaux")

    # Filtrage
    recos = df.copy()
    recos = recos[recos['lieu'] == lieu]
    if animaux: recos = recos[recos['animaux_safe'] == "Oui"]
    if expo: recos = recos[recos['lumiere'] == expo]

    st.markdown("---")
    st.subheader(f"✨ Notre sélection {lieu} :")
    
    if recos.empty:
        st.info("Aucune plante ne correspond exactement. Demandez à nos experts !")
    else:
        for _, row in recos.head(5).iterrows():
            st.markdown(f"""
                <div class="reco-card">
                    <h3 style="margin:0; text-align:left;">{row['nom']}</h3>
                    <p style="font-size: 14px; margin-top:10px;">🚿 <b>Entretien :</b> {row['entretien']}</p>
                    <p style="font-size: 14px; background: #fff; padding: 10px; border-radius: 5px; margin-top:5px;">💡 {row['conseil']}</p>
                </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
