import psycopg2
import bcrypt

# Fonction de connexion à la base PostgreSQL
def connect():
    return psycopg2.connect(
        host="localhost",
        dbname="PFE",
        user="postgres",
        password="0000"  
    )


#Vérifier si un utilisateur existe déjà
def user_exists(email):
    conn = connect()
    cursor = conn.cursor() #créer un curseur qui sert à exécuter des requêtes SQL
    cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists


# Enregistrer un nouvel utilisateur avec mot de passe hashé
def register_user(nom, prenom, email, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (nom, prenom, email, password)
        VALUES (%s, %s, %s, %s)
    """, (nom, prenom, email, hashed.decode('utf-8')))
    conn.commit()
    cur.close()
    conn.close()


# Vérifier les identifiants à la connexion
def login_user(email, password):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT prenom, password FROM users WHERE email = %s", (email,))
    result = cursor.fetchone() #récupère une seule ligne du résultat de la requête.

    cursor.close()
    conn.close()

    if result:
        nom_utilisateur, hashed_pw = result
        if bcrypt.checkpw(password.encode('utf-8'), hashed_pw.encode('utf-8')):
            token = generate_token(email)
            return nom_utilisateur, token

    return None, None



#Génération du token JWT
import jwt
import datetime

SECRET_KEY = "supersecret"  

def generate_token(email):
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60) #date d’expiration dans 60 minutes
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")



# fonction permet de décoder un token (JWT) et vérifier s’il est valide et non expiré
def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded  # contient l'email et la date d’expiration
    except jwt.ExpiredSignatureError:
        return None  # Token expiré
    except jwt.InvalidTokenError:
        return None  # Token invalide
