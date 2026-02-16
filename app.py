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
        margin-right: 20px;
        width: 100px;
        height: 100px;
        object-fit: cover;
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

# --- LOGO ---
# On utilise le logo haute résolution que vous avez fourni
if os.path.exists("logo.png"):
    st.image("logo.png", width=250)
else:
    st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", width=250)

st.title("Votre Coach Main Verte Personnel 🌿")

# --- CHARGEMENT ---
@st.cache_data
def load_data():
    df = pd.read_csv("plantes.csv")
    return df

@st.cache_data
def load_villes():
    return pd.read_csv("config.csv")['ville'].tolist()

df = load_data()
villes = load_villes()

# --- LOGIQUE ---
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
    st.subheader("Vos recommandations personnalisées :")
    
    # --- FILTRES SIMPLIFIÉS ---
    c1, c2 = st.columns(2)
    with c1:
        expo = st.radio("Lumière chez vous :", ["Ombre", "Vive", "Directe"])
    with c2:
        animaux = st.toggle("🐱 J'ai des animaux")

    recos = df.copy()
    if animaux: recos = recos[recos['animaux_safe'] == "Oui"]
    if expo: recos = recos[recos['lumiere'] == expo]

    st.markdown("---")

    if recos.empty:
        st.info("Aucune plante ne correspond pile à vos critères. Nos experts sont là pour vous aider !")
    else:
        for _, row in recos.head(3).iterrows():
            # GENERATEUR D'IMAGE AUTOMATIQUE SI VIDE
            nom_plante = row['nom'].replace(' ', '+')
            img_url = f"https://loremflickr.com/320/320/plant,{nom_plante}/all"
            
            st.markdown(f"""
                <div class="reco-card">
                    <img src="{img_url}" alt="Plante" />
                    <div>
                        <h3 style="margin:0; text-align:left;">{row['nom']}</h3>
                        <p style="font-size: 14px; margin-top:5px;">💡 {row['conseil']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
