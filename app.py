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
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.05);
    }
    
    /* Image dans la carte */
    .reco-card img {
        border-radius: 10px;
        margin-right: 20px;
        width: 100px;
        height: 100px;
        object-fit: cover;
        border: 1px solid #eee;
    }
    
    /* Texte dans la carte */
    .reco-content { flex-grow: 1; }
    
    /* Boutons */
    .stButton>button { 
        background-color: var(--rouge-pa) !important; 
        color: white !important; 
        border-radius: 30px !important; 
        border: none !important;
        padding: 12px 30px !important;
        width: 100%;
        font-weight: bold !important;
        font-size: 18px !important;
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

try:
    df = load_data()
    villes = load_villes()
except:
    st.error("Erreur de lecture. Vérifiez que plantes.csv possède bien les colonnes : nom,categorie,entretien,lumiere,animaux_safe,conseil,image_url")
    st.stop()

# --- ENTÊTE AVEC LOGO CENTRÉ ---
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
with col_logo_2:
    # On teste tous les noms de fichiers possibles pour le logo
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo plantes addict Haute Résolution .png"):
        st.image("logo plantes addict Haute Résolution .png", use_container_width=True)
    else:
        st.image("https://www.plantesaddict.fr/img/logo-plantes-addict.png", use_container_width=True)

st.title("Votre Coach Main Verte Personnel 🌿")

# --- GESTION DES ÉTAPES ---
if 'etape' not in st.session_state:
    st.session_state.etape = 'accueil'

# --- ÉCRAN 1 : ACCUEIL ---
if st.session_state.etape == 'accueil':
    st.write("### 🏠 Bienvenue à la vente !")
    email = st.text_input("Votre email :", placeholder="exemple@email.com")
    ville = st.selectbox("Ville actuelle :", villes)
    
    if st.button("Lancer mon diagnostic"):
        if email and "@" in email:
            st.session_state.email = email
            st.session_state.ville = ville
            st.session_state.etape = 'diagnostic'
            st.rerun()
        else:
            st.warning("Entrez un email valide.")

# --- ÉCRAN 2 : LE DIAGNOSTIC ---
elif st.session_state.etape == 'diagnostic':
    st.write(f"📍 Boutique : **{st.session_state.ville}**")
    st.subheader("Quelle plante est faite pour vous ?")
    
    c1, c2 = st.columns(2)
    with c1:
        expo = st.radio("Lumière chez vous :", ["Ombre", "Vive", "Directe"])
    with c2:
        animaux = st.toggle("🐱 J'ai des animaux")

    recos = df.copy()
    if animaux:
        recos = recos[recos['animaux_safe'] == "Oui"]
    if expo:
        recos = recos[recos['lumiere'] == expo]

    st.markdown("---")
    st.subheader("✨ Nos recommandations :")

    if recos.empty:
        st.info("Aucune plante ne correspond exactement. Demandez à nos experts sur place !")
    else:
        for _, row in recos.head(3).iterrows():
            # Sécurité pour l'image : si la colonne manque ou est vide
            img_url = "https://www.plantesaddict.fr/img/logo-plantes-addict.png"
            if 'image_url' in row and pd.notna(row['image_url']):
                img_url = row['image_url']
            
            st.markdown(f"""
                <div class="reco-card">
                    <img src="{img_url}" alt="Plante" />
                    <div class="reco-content">
                        <h3 style="margin:0; text-align:left;">{row['nom']}</h3>
                        <p style="font-size: 14px; margin-top: 10px;">🚿 <b>Entretien :</b> {row['entretien']}</p>
                        <p style="font-size: 14px; background: #fff; padding: 10px; border-radius: 5px; margin-top:5px;">💡 <b>Conseil :</b> {row['conseil']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Recommencer"):
        st.session_state.etape = 'accueil'
        st.rerun()

st.markdown("<br><hr><center><p style='color: #999; font-size: 12px;'>© Plantes Addict</p></center>", unsafe_allow_html=True)
