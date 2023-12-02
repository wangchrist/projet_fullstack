from fastapi import FastAPI, Request,Form,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from clean import clean_data
from insert import fill_db
import psycopg2
from psycopg2 import sql


app = FastAPI() 

templates = Jinja2Templates(directory="templates")
clean_data() ## nettoyage des données
fill_db()
db_params = {
     'dbname': 'mydatabase',
     'user': 'myuser',
     'password': 'mypassword',
     'host': 'database',
     'port': '5432',
}
def verify_credentials(username: str, password: str):
    try:
        # Établir une connexion à la base de données
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Exécuter une requête pour vérifier les identifiants
        query = sql.SQL("""
            SELECT * FROM utilisateur WHERE identifiant = %s AND mdp = %s
        """)
        cursor.execute(query, (username, password))
        
        # Récupérer le résultat
        user = cursor.fetchone()

        # Fermer la connexion à la base de données
        cursor.close()
        conn.close()

        return user is not None
    except Exception as e:
        print(f"Erreur lors de la vérification des identifiants : {e}")
        return False

def user_exists(username: str, cursor):
    # Vérifier si l'utilisateur existe déjà dans la base de données
    query = sql.SQL("""
        SELECT 1 FROM utilisateur WHERE identifiant = %s
    """)
    cursor.execute(query, (username,))
    return cursor.fetchone() is not None

def create_user(username: str, password: str):
    try:
        # Établir une connexion à la base de données
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Vérifier si l'utilisateur existe déjà
        if user_exists(username, cursor):
            raise HTTPException(status_code=400, detail="L'utilisateur existe déjà")

        # Exécuter une requête pour insérer un nouvel utilisateur
        query = sql.SQL("""
            INSERT INTO utilisateur (identifiant, mdp) VALUES (%s, %s)
        """)
        cursor.execute(query, (username, password))

        # Committer les changements et fermer la connexion à la base de données
        conn.commit()
        cursor.close()
        conn.close()

        return True
    except HTTPException:
        # Intercepter l'exception HTTPException et la relancer
        raise
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur : {e}")
        return False
# def query_user(username):
#     connection = psycopg2.connect(**db_params)
#     cursor = connection.cursor()

#     select_query = sql.SQL("SELECT * FROM utilisateur WHERE identifiant = {}").format(sql.Literal(username))
#     cursor.execute(select_query)

#     user = cursor.fetchone()

#     cursor.close()
#     connection.close()

#     return user

@app.get("/", response_class=HTMLResponse) 
async def root(request: Request):
     
    return templates.TemplateResponse("accueil.html", {"request": request})

@app.get("/inscription", response_class=HTMLResponse) 
async def inscription(request: Request):
    return templates.TemplateResponse("inscription.html", {"request": request})

@app.get("/connexion", response_class=HTMLResponse) 
async def connexion(request: Request):
    return templates.TemplateResponse("connexion.html", {"request": request})
# Route pour traiter la soumission du formulaire
@app.post("/connexion", response_class=HTMLResponse)
async def process_connexion_form(request: Request,username: str = Form(...), password: str = Form(...)):
    # Vérifier les identifiants en appelant la fonction verify_credentials
    if verify_credentials(username, password):
        # Redirection en cas de succès
        return templates.TemplateResponse("aff.html", {"request": request, "username": username})
    else:
        # Gérer le cas d'échec (par exemple, afficher un message d'erreur)
        return templates.TemplateResponse("connexion.html", {"request": request, "error_message": "Identifiants incorrects ou n'existent pas"})

@app.post("/inscription", response_class=HTMLResponse)
async def process_inscription_form( request: Request,username: str = Form(...), password: str = Form(...)):
    # Créer un nouvel utilisateur en appelant la fonction create_user
    try:
        if create_user(username, password):
            # Redirection en cas de succès (par exemple, vers une page de connexion)
            return templates.TemplateResponse("connexion.html", {"request": request, "success_message": "Inscription réussie. Connectez-vous maintenant."})
    except HTTPException as e:
        # Gérer l'exception HTTPException (par exemple, afficher un message d'erreur)
        return templates.TemplateResponse("inscription.html", {"request": request, "error_message": str(e)})

    # Gérer le cas d'échec (par exemple, afficher un message d'erreur générique)
    return templates.TemplateResponse("inscription.html", {"request": request, "error_message": "Erreur lors de l'inscription. Veuillez réessayer."})