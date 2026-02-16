import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Plantes Addict - Coach Main Verte", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- DESIGN PERSONNALISÉ (ROUGE PLANTES ADDICT) ---
st.markdown("""
    <style>
    /* Couleurs principales */
    :root {
        --rouge-pa: #e2001a;
    }
    .stApp { background-color: #ffffff; }
    
    /* Titres */
    h1, h2, h3 { 
        color: var(--rouge-pa) !important; 
        font-family: 'Helvetica Neue', sans-serif;
        text-align: center;
    }
    
    /* Cartes de recommandations */
    .reco-card { 
        border: 2px solid var(--rouge-pa); 
        background: #fffafa; 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 20px;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.05);
    }
    
    /* Boutons */
    .stButton>button { 
        background-color: var(--rouge-pa) !important; 
        color: white !important; 
        border-radius: 30px !important; 
        border: none !important;
        padding: 12px 30px !important;
        width: 100%;
        font-size: 18px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(226, 0, 26, 0.3);
    }

    /* Inputs */
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    return pd.read_csv("plantes.csv")

@st.cache_data
def load_villes():
    return pd.read_csv("config.csv")['ville'].tolist()

try:
    df = load_data()
    villes = load_villes()
except Exception as e:
    st.error("Erreur de chargement des fichiers CSV. Vérifiez plantes.csv et config.csv sur GitHub.")
    st.stop()

# --- AFFICHAGE DU LOGO ---
# On vérifie si un logo local existe, sinon on prend l'URL du site
if os.path.exists("logo.png"):
    st.image("logo.png", width=250)
else:
    # URL de secours
    st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", width=250)

st.title("Votre Coach Main Verte Personnel 🌿")
st.markdown("<p style='text-align: center; color: #666;'>Trouvez la plante parfaite pour votre intérieur en 30 secondes.</p>", unsafe_allow_html=True)

# --- SYSTÈME D'ÉTAPE ---
if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRAN 1 : ACCUEIL & EMAIL ---
if st.session_state.etape == 'accueil':
    with st.container():
        st.write("### 🏠 Bienvenue à la vente !")
        email = st.text_input("Entrez votre email pour commencer :", placeholder="exemple@email.com")
        ville = st.selectbox("Dans quelle ville êtes-vous ?", villes)
        
        if st.button("Lancer mon diagnostic gratuit"):
            if email and "@" in email:
                st.session_state.email = email
                st.session_state.ville = ville
                st.session_state.etape = 'diagnostic'
                st.rerun()
            else:
                st.warning("Veuillez entrer une adresse email valide.")

# --- ÉCRAN 2 : LE DIAGNOSTIC ---
elif st.session_state.etape == 'diagnostic':
    st.write(f"📍 **Vente de {st.session_state.ville}**")
    
    st.subheader("Quel est votre environnement ?")
    
    col1, col2 = st.columns(2)
    with col1:
        expo = st.radio("Lumière disponible :", ["Ombre", "Vive", "Directe"])
        taille = st.multiselect("Format souhaité :", ["Petite", "Moyenne", "Grande"])
    
    with col2:
        niveau = st.select_slider("Votre expérience :", options=["Débutant", "Habitué", "Expert"])
        animaux = st.toggle("🐱 J'ai des animaux (Safe)")

    # Filtrage
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
        st.info("Aucune plante ne correspond pile à vos critères. Demandez conseil à nos experts sur place !")
    else:
        # On affiche les 3 meilleures correspondances
        for _, row in recos.head(3).iterrows():
            st.markdown(f"""
                <div class="reco-card">
                    <h3 style="margin:0; text-align:left;">{row['nom']}</h3>
                    <p style="color: #e2001a; font-weight: bold; margin: 5px 0;">💰 {row['prix']}</p>
                    <p style="font-size: 14px; margin-bottom: 5px;">🚿 <b>Entretien :</b> {row['entretien']}</p>
                    <p style="font-size: 14px; background: #fff; padding: 10px; border-radius: 5px;">💡 <b>Le conseil du coach :</b> {row['conseil']}</p>
                </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Recommencer le test"):
        st.session_state.etape = 'accueil'
        st.rerun()

# --- FOOTER ---
st.markdown("<br><hr><center><p style='color: #999; font-size: 12px;'>© 2026 Plantes Addict - Ventes éphémères partout en France</p></center>", unsafe_allow_html=True)
