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
    h1, h3 { color: var(--rouge-pa) !important; text-align: center; }
    .reco-card { 
        border: 2px solid var(--rouge-pa); 
        background: #fffafa; 
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    .reco-card img {
        border-radius: 10px;
        margin-right: 15px;
        width: 120px;
        height: 120px;
        object-fit: cover; /* Recadre l'image proprement */
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

# --- CHARGEMENT ---
@st.cache_data
def load_data():
    return pd.read_csv("plantes.csv")

@st.cache_data
def load_villes():
    return pd.read_csv("config.csv")['ville'].tolist()

df = load_data()
villes = load_villes()

# --- LOGO ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=220)
else:
    st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", width=220)

st.title("Votre Coach Main Verte Personnel 🌿")

# --- NAVIGATION ---
if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

if st.session_state.etape == 'accueil':
    st.write("### 🏠 Bienvenue !")
    email = st.text_input("Votre email :")
    ville = st.selectbox("Ville :", villes)
    if st.button("Lancer mon diagnostic"):
        if "@" in email:
            st.session_state.email = email
            st.session_state.ville = ville
            st.session_state.etape = 'diagnostic'
            st.rerun()

elif st.session_state.etape == 'diagnostic':
    st.subheader("Vos préférences :")
    c1, c2 = st.columns(2)
    with c1:
        expo = st.radio("Lumière :", ["Ombre", "Vive", "Directe"])
        taille = st.multiselect("Format :", ["Petite", "Moyenne", "Grande"])
    with c2:
        animaux = st.toggle("🐱 Spécial Animaux")

    recos = df.copy()
    if animaux: recos = recos[recos['animaux_safe'] == "Oui"]
    if expo: recos = recos[recos['lumiere'] == expo]
    if taille: recos = recos[recos['categorie'].isin(taille)]

    st.markdown("---")
    st.subheader("✨ Vos recommandations :")

    if recos.empty:
        st.info("Demandez à nos experts sur place !")
    else:
        for _, row in recos.head(3).iterrows():
            # SOLUTION AUTOMATIQUE POUR LES IMAGES :
            # Si 'image_url' n'existe pas ou est vide, on cherche sur Unsplash par nom de plante
            img_url = row.get('image_url')
            if pd.isna(img_url) or img_url == "":
                # On utilise une image générique basée sur le nom de la plante
                img_url = f"https://source.unsplash.com/featured/?{row['nom'].replace(' ', '')},plant"
            
            st.markdown(f"""
                <div class="reco-card">
                    <img src="{img_url}" />
                    <div>
                        <h3 style="margin:0; text-align:left;">{row['nom']}</h3>
                        <p style="font-size: 14px; margin-top:5px;">💡 {row['conseil']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
