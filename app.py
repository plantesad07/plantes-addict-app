import streamlit as st
import pandas as pd

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Plantes Addict - Coach Main Verte", layout="centered")

# Design aux couleurs de Plantes Addict (Rouge et Blanc)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    /* Titres et textes */
    h1, h2, h3 { color: #e2001a !important; font-family: 'Helvetica', sans-serif; }
    
    /* Cartes de recommandations */
    .reco-card { 
        border: 2px solid #e2001a; 
        background: #fff5f5; 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 20px;
    }
    
    /* Boutons personnalisés en Rouge Plantes Addict */
    .stButton>button { 
        background-color: #e2001a !important; 
        color: white !important; 
        border-radius: 30px !important; 
        border: none !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
    }
    
    /* Alerte de toxicité */
    .toxic-warning {
        background-color: #ffeded;
        color: #cc0000;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        border: 1px solid #cc0000;
        margin-top: 5px;
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

# --- ENTÊTE AVEC LOGO ---
# Utilisation de l'image de votre site pour le logo
st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", width=220)
st.title("Votre Coach Main Verte Personnel 🌿")
st.markdown("---")

# --- ÉTAPE 1 : ACCÈS AU COACH ---
if 'auth' not in st.session_state:
    st.subheader("Bénéficiez de conseils sur-mesure")
    with st.form("auth_form"):
        email = st.text_input("Votre email pour recevoir le récapitulatif :")
        ville = st.selectbox("Où nous trouvez-vous aujourd'hui ?", villes)
        submit = st.form_submit_button("Lancer mon diagnostic gratuit")
        
        if submit:
            if "@" in email:
                st.session_state.auth = True
                st.session_state.ville = ville
                st.rerun()
            else:
                st.error("Oups ! Il nous faut un email valide.")
    st.stop()

# --- ÉTAPE 2 : LE DIAGNOSTIC ---
st.write(f"📍 En direct de la vente de : **{st.session_state.ville}**")

st.subheader("Dites-nous tout...")
c1, c2 = st.columns(2)
with c1:
    expo = st.radio("Exposition de votre pièce :", ["Ombre", "Vive", "Directe"])
    exp_client = st.select_slider("Votre niveau :", options=["Débutant", "Habitué", "Expert"])

with c2:
    pet_friendly = st.toggle("🐱 J'ai des animaux")
    taille = st.multiselect("Taille souhaitée :", ["Petite", "Moyenne", "Grande"])

# --- FILTRAGE ---
results = df.copy()
if pet_friendly:
    results = results[results['animaux_safe'] == "Oui"]
if expo:
    results = results[results['lumiere'] == expo]
if taille:
    results = results[results['categorie'].isin(taille)]

# --- RÉSULTATS ---
st.markdown("### ✨ Nos pépites pour vous :")

if results.empty:
    st.info("Aucune correspondance exacte, mais n'hésitez pas à demander à nos experts en t-shirt rouge sur place !")
else:
    for _, row in results.head(3).iterrows():
        with st.container():
            st.markdown(f"""
                <div class="reco-card">
                    <h3 style="margin-top:0;">{row['nom']}</h3>
                    <p><b>💰 Prix : {row['prix']}</b></p>
                    <p>🚿 <b>Entretien :</b> {row['entretien']}</p>
                    <p>💡 <b>Conseil :</b> {row['conseil']}</p>
                </div>
            """, unsafe_allow_html=True)

if st.button("🔄 Recommencer le test"):
    del st.session_state.auth
    st.rerun()

st.markdown("---")
st.caption("© Plantes Addict - Tous droits réservés")
