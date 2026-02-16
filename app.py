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
    .badge-froid {
        background-color: #007bff;
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 10px;
    }
    .stButton>button { 
        background-color: var(--rouge-pa) !important; 
        color: white !important; 
        border-radius: 30px !important; 
        width: 100%;
        font-weight: bold !important;
        height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO CENTRÉ ---
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
with col_logo_2:
    # On utilise le logo officiel en ligne pour être sûr qu'il s'affiche
    st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", use_container_width=True)

st.title("Votre Coach Main Verte Personnel 🌿")

# --- CHARGEMENT ---
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
    st.error(f"Erreur de lecture : {e}")
    st.stop()

if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRAN 1 : ACCUEIL ---
if st.session_state.etape == 'accueil':
    st.write("### 🏠 Bienvenue à la vente !")
    email = st.text_input("Votre email :")
    ville = st.selectbox("Choisissez votre ville :", villes_list)
    if st.button("Lancer mon diagnostic"):
        if email and "@" in email:
            st.session_state.email = email
            st.session_state.ville = ville
            st.session_state.etape = 'diagnostic'
            st.rerun()

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
        st.info("Aucune plante ne correspond exactement. Demandez à nos experts !")
    else:
        for _, row in recos.iterrows():
            froid_info = ""
            # On affiche le badge froid si c'est une plante d'extérieur
            if lieu == "Extérieur" and 'resistance' in row and pd.notna(row['resistance']):
                froid_info = f'<div class="badge-froid">❄️ Résiste jusqu\'à {row["resistance"]}</div>'

            # AFFICHAGE DE LA CARTE (Correction unsafe_allow_html ajoutée)
            st.markdown(f"""
                <div class="reco-card">
                    {froid_info}
                    <h3 style="margin:0; text-align:left;">{row['nom']}</h3>
                    <p style="font-size: 14px; margin-top:10px;">🚿 <b>Entretien :</b> {row['entretien']}</p>
                    <p style="font-size: 14px; background: #fff; padding: 10px; border-radius: 5px; margin-top:5px;">💡 {row['conseil']}</p>
                </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()
