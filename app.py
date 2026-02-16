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
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.05);
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

# --- LOGO CENTRÉ ---
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
with col_logo_2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo plantes addict Haute Résolution .png"):
        st.image("logo plantes addict Haute Résolution .png", use_container_width=True)
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

try:
    df = load_data()
    villes = load_villes()
except:
    st.error("Vérifiez que vos fichiers CSV sont bien sur GitHub.")
    st.stop()

if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRANS ---
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

elif st.session_state.etape == 'diagnostic':
    st.write(f"📍 Vente : **{st.session_state.ville}**")
    c1, c2 = st.columns(2)
    with c1:
        expo = st.radio("Lumière :", ["Ombre", "Vive", "Directe"])
    with c2:
        animaux = st.toggle("🐱 J'ai des animaux")

    recos = df.copy()
    if animaux: recos = recos[recos['animaux_safe'] == "Oui"]
    if expo: recos = recos[recos['lumiere'] == expo]

    st.markdown("---")
    
    if recos.empty:
        st.info("Aucune correspondance exacte. Demandez conseil à nos experts sur place !")
    else:
        for _, row in recos.head(3).iterrows():
            # Utilisation de l'image réelle ou logo par défaut
            img_url = row['image_url'] if pd.notna(row['image_url']) else "https://www.plantesaddict.fr/img/logo-plantes-addict.png"
            
            st.markdown(f"""
                <div class="reco-card">
                    <img src="{img_url}" onerror="this.src='https://www.plantesaddict.fr/img/logo-plantes-addict.png'"/>
                    <div style="flex-grow:1;">
                        <h3 style="margin:0; text-align:left;">{row['nom']}</h3>
                        <p style="font-size: 14px; margin-top:10px;">🚿 <b>Entretien :</b> {row['entretien']}</p>
                        <p style="font-size: 14px; background: #fff; padding: 10px; border-radius: 5px; margin-top:5px;">💡 {row['conseil']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
