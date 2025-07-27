import streamlit as st
import base64
st.set_page_config(page_title="website", layout="wide")


# Initialisation de l'état
if "page" not in st.session_state:
    st.session_state.page = "Accueil"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"


# Fonction pour afficher une image en arrière-plan de la sidebar
from PIL import Image

def set_sidebar_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    css = f"""
    <style>
    [data-testid="stSidebar"] {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    /* Le titre principal de la sidebar */
    [data-testid="stSidebar"] h5 {{
        color: white !important;
        font-size: 30px !important;
        font-weight: bold;
        text-align: center;
        margin-top: 30px;
    }}
    /* Overlay sombre semi-transparent pour améliorer la lisibilité */
    [data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.3);  /* Ombre noire semi-transparente */
        z-index: 0;
    }}
    /* Bouton de déconnexion */
    [data-testid="stSidebar"] button {{
        background-color: #007B8A !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        margin-bottom: 20px;
        width: 100%;
    }}

    [data-testid="stSidebar"] * {{
        color: black !important;
    }}
    .logout-button {{
        position: absolute;
        bottom: 20px;
        left: 10%;
        width: 80%;
        text-align: center;
    }}
    .logout-button button {{
        background-color: #007B8A !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        width: 100%;
    }}


    /* Spécifiquement pour le texte du selectbox */
    div[data-baseweb="select"] div {{
        color: black !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Appel dans le script principal
set_sidebar_background("navigation.jpg")

# Barre de navigation avec titre personnalisé
st.sidebar.markdown("""
    <style>
        [data-testid="stSidebar"] h1 {
            color: white !important;
            font-size: 36px !important;
            font-weight: bold;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("# Welcome to Your Analyst Workspace")

menu = ["Accueil", "Dashboards", "BankBot Q-A", "Contact"]
choice = st.sidebar.selectbox("", menu, index=menu.index(st.session_state.page))

# Vérifie si l'utilisateur est connecté
if "token" in st.session_state:
    st.sidebar.markdown('<div class="logout-button">', unsafe_allow_html=True)
    if st.sidebar.button("🔓 Se déconnecter"):
        for key in ["token", "page", "auth_mode"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Fonction : formulaire de connexion
import re #sert à utiliser les expressions régulières pour vérifier les coordonnées

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def login_form():
    st.subheader("Connexion")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):
        if not email or not password:
            st.warning("Veuillez remplir tous les champs.")
        elif not is_valid_email(email):
            st.warning("Veuillez entrer un email valide.")
        elif len(password) < 6:
            st.warning("Le mot de passe doit contenir au moins 6 caractères.")
        else:
            # Authentification avec retour prénom + token
            prenom, token = database.login_user(email, password)
            if prenom and token:
                st.success("Connexion réussie.")
                # Sauvegarde en session sécurisée
                st.session_state.page = "Dashboards"
                st.session_state.token = token
                st.session_state.prenom = prenom
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    if st.button("Créer un compte"):
        st.session_state.auth_mode = "signup"
        st.rerun()


import database
import re  # pour valider l’email

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)
# Fonction : formulaire d'inscription
def signup_form():
    st.subheader("Créer un compte")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le mot de passe", type="password")

    if st.button("S'inscrire"):
        # Vérification des champs obligatoires
        if not nom or not prenom or not email or not password or not confirm_password:
            st.error("Veuillez remplir tous les champs.")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("Veuillez saisir un email valide.")
        elif len(password) < 6:
            st.error("Le mot de passe doit contenir au moins 6 caractères.")
        elif password != confirm_password:
            st.error("Les mots de passe ne correspondent pas.")
        else:
            try:
                # Vérification si l'email existe déjà
                if database.user_exists(email):
                    st.error("Cet utilisateur est déjà inscrit. Veuillez vous connecter.")
                else:
                    database.register_user(nom, prenom, email, password)
                    st.success("Inscription réussie ! Vous pouvez maintenant vous connecter.")
                    st.session_state.auth_mode = "login"
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de l'enregistrement : {e}")
    if st.button("🔁 Déjà inscrit ? Connectez-vous"):
        st.session_state.auth_mode = "login"
        st.rerun()
        
# Page d'accueil = login/signup 
if choice == "Accueil":
    if st.session_state.auth_mode == "login":
        login_form()
    else:
        signup_form()

elif choice == "Dashboards":
    # Vérification de l'accès protégé
    if "token" not in st.session_state:
        st.error("⛔ Accès refusé. Veuillez vous connecter d'abord.")
        st.stop()  # interrompt l'exécution ici
    st.markdown("""
        <iframe title="Dashboard Transactions"
                width="1000"
                height="600"
                src="https://app.powerbi.com/view?r=eyJrIjoiNjViZWNkZjItYWY0NC00YTAxLWIyNTAtZjMyNTk5MTQ4NTBiIiwidCI6ImRiZDY2NjRkLTRlYjktNDZlYi05OWQ4LTVjNDNiYTE1M2M2MSIsImMiOjl9"
                frameborder="0"
                allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)

elif choice == "BankBot Q-A":
    # Vérification de l'accès protégé
    if "token" not in st.session_state:
        st.error("⛔ Accès refusé. Veuillez vous connecter d'abord.")
        st.stop()  # interrompt l'exécution ici

    # Titre centré (en noir)
    st.markdown("<h1 style='text-align: center; color: black;'>💬 BankBot Q-A</h1>", unsafe_allow_html=True)

    # Description (centrée, noire)
    st.markdown("""
        <p style='text-align: center; font-size:18px; color: black;'>
        Posez vos questions à notre agent virtuel intelligent !<br>
        🔍 Anomalies, 💰 Montants, 👥 Clients, 🌍 Transactions suspectes...
        </p>
    """, unsafe_allow_html=True)

    # Animation Lottie agrandie
    lottie_animation = """
    <script src="https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs" type="module"></script> 
    <div style="display: flex; justify-content: center;">
        <dotlottie-player 
            src="https://lottie.host/80371b4f-2646-4b90-94f9-ea25e47b7c1b/CBciRZVhLx.lottie" 
            background="transparent" 
            speed="1" 
            style="width: 500px; height: 500px;" 
            loop 
            autoplay>
        </dotlottie-player>
    </div>
    """
    st.components.v1.html(lottie_animation, height=520)

    # Chatbot Dialogflow
    chatbot_code = """
        <div style="display: flex; justify-content: center; margin-top: 30px;">
            <script src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"></script>
            <df-messenger
                intent="WELCOME"
                chat-title="BanqueBot"
                agent-id="7fe0bccc-027b-4b11-bb9e-7fbc568d5963"
                language-code="fr">
            </df-messenger>
        </div>
    """
    st.components.v1.html(chatbot_code, height=600)


   

elif choice == "Contact":
    st.markdown("""
        <div class="contact-background">
            <h2> Contactez Amen Bank </h2>
            <p>Siège social : (+216) 71 148 000</p>
            <p>Salle des Marchés : (+216) 31 348 000</p>
            <p>Centre de Relations Clients : (+216) 71 148 888</p>
            <p><strong> crc@amenbank.com.tn</strong></p>
            <p>Avenue Mohamed V - 1002 Tunis</p>
            
        </div>
        <div class="map-container">
           <iframe
           src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3194.266941293405!2d10.181487375645776!3d36.81212277224373!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x12fd34637a4561c5%3A0xff2456e9abb14f93!2zQW1lbiBCYW5rIC0g2KjZhtmDINin2YTYo9mF2KfZhg!5e0!3m2!1sfr!2stn!4v1745090148316!5m2!1sfr!2stn" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade">"
           width="100%"
           height="400"
           style="border:0;"
           allowfullscreen=""
           loading="lazy"
           referrerpolicy="no-referrer-when-downgrade">
           </iframe>
        </div>
        
    """, unsafe_allow_html=True)