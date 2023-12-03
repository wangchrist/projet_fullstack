from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import psycopg2
from psycopg2 import sql
from clean import clean_data
from insert import fill_db
from fastapi import Query

app = FastAPI() 

clean_data()
fill_db()

templates = Jinja2Templates(directory="templates")

db_params = {
    'dbname': 'mydatabase',
    'user': 'myuser',
    'password': 'mypassword',
    'host': 'database',
    'port': '5432',
}

conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

def verify_credentials(username: str, password: str):
    try:

        # Exécuter une requête pour vérifier les identifiants
        query = sql.SQL("""
            SELECT * FROM utilisateur WHERE identifiant = %s AND mdp = %s
        """)
        cursor.execute(query, (username, password))
        
        # Récupérer le résultat
        user = cursor.fetchone()

        return user is not None
    except Exception as e:
        print(f"Erreur lors de la vérification des identifiants : {e}")
        return False
    
def user_exists(username: str):
    # Vérifier si l'utilisateur existe déjà dans la base de données
    query = sql.SQL("""
        SELECT 1 FROM utilisateur WHERE identifiant = %s
    """)
    cursor.execute(query, (username,))
    return cursor.fetchone() is not None

def create_user(username: str, password: str):
    try:

        # Vérifier si l'utilisateur existe déjà
        if user_exists(username):
            raise HTTPException(status_code=400, detail="L'utilisateur existe déjà")

        # Exécuter une requête pour insérer un nouvel utilisateur
        query = sql.SQL("""
            INSERT INTO utilisateur (identifiant, mdp) VALUES (%s, %s)
        """)
        cursor.execute(query, (username, password))

        return True
    except HTTPException:
        # Intercepter l'exception HTTPException et la relancer
        raise
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur : {e}")
        return False

def update_liste(event_name: str, username: str):
    try:
        query = sql.SQL("""
            SELECT id FROM evenement WHERE titre = %s
        """)
        cursor.execute(query, (event_name,))
        event_id = cursor.fetchone()

        query = sql.SQL("""
            SELECT id FROM utilisateur WHERE identifiant = %s
        """)
        cursor.execute(query, (username,))
        user_id = cursor.fetchone()

        query = sql.SQL("""
            INSERT INTO liste (id_evenement, id_utilisateur) VALUES (%s, %s)
        """)
        cursor.execute(query, (event_id[0],user_id[0]))
        conn.commit()
                
    except Exception as e:
        print(f"Error updating liste: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/", response_class=HTMLResponse) 
async def root(request: Request):
    return templates.TemplateResponse("accueil.html", {"request": request})

@app.get("/inscription", response_class=HTMLResponse) 
async def inscription(request: Request):
    return templates.TemplateResponse("inscription.html", {"request": request})

@app.get("/connexion", response_class=HTMLResponse) 
async def connexion(request: Request):
    return templates.TemplateResponse("connexion.html", {"request": request})

@app.post("/connexion", response_class=HTMLResponse)
async def process_connexion_form(request: Request,username: str = Form(...), password: str = Form(...)):
    # Vérifier les identifiants en appelant la fonction verify_credentials
    if verify_credentials(username, password):
        # Redirection en cas de succès
        # return templates.TemplateResponse("tableau_de_bord.html", {"request": request, "username": username})
        return RedirectResponse(url=f"/tableau_de_bord?username={username}", status_code=303)
    else:
        # Gérer le cas d'échec (par exemple, afficher un message d'erreur)
        return templates.TemplateResponse("connexion.html", {"request": request, "error_message": "Identifiants incorrects ou n'existent pas"})

@app.post("/inscription", response_class=HTMLResponse)
async def process_inscription_form( request: Request,username: str = Form(...), password: str = Form(...)):
    # Créer un nouvel utilisateur en appelant la fonction create_user
    try:
        if create_user(username, password):
            # Redirection en cas de succès (par exemple, vers une page de connexion)
            return RedirectResponse(url="/connexion", status_code=303)
    except HTTPException as e:
        # Gérer l'exception HTTPException (par exemple, afficher un message d'erreur)
        error_message = str(e.detail)
        return templates.TemplateResponse("inscription.html", {"request": request, "error_message": error_message})

    # Gérer le cas d'échec (par exemple, afficher un message d'erreur générique)
    return templates.TemplateResponse("inscription.html", {"request": request, "error_message": "Erreur lors de l'inscription. Veuillez réessayer."})

@app.get("/tableau_de_bord", response_class=HTMLResponse) 
async def tableau_de_bord(request: Request):
    try:
        query = sql.SQL("""
        SELECT titre, chapeau, date_de_debut, date_de_fin, description_de_la_date, mots_cles, nom_du_lieu, adresse_du_lieu, 
                        code_postal, ville, url_de_contact, telephone_de_contact, email_de_contact, type_de_prix, detail_du_prix, 
                        type_dacces, url_de_reservation, audience FROM evenement
        """)
        cursor.execute(query)
        results = cursor.fetchall()
        events = [(result[0], result[1], result[2], result[3],result[4],result[5], result[6], result[7], result[8],result[9],
                   result[10], result[11], result[12], result[13],result[14],result[15], result[16], result[17]) for result in results]
        return templates.TemplateResponse("tableau_de_bord.html", {"request": request, "events": events})
    
    except psycopg2.Error as e:
        print("Error:", e)
        events = []
    return templates.TemplateResponse("tableau_de_bord.html", {"request": request})


@app.post("/tableau_de_bord", response_class=HTMLResponse)
async def process_events_form(request: Request, selected_events: list = Form(...), username: str = Query(..., alias="username")):
    try:
        for event_name in selected_events:
            update_liste(event_name, username)

        return RedirectResponse(url=f"/tableau_de_bord?username={username}", status_code=303)

    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": str(e)})
    

@app.get("/traiter-formulaire", response_class=HTMLResponse)
async def process_events_form(request: Request, username: str = Query(..., alias="username")):
    
    return RedirectResponse(url=f"/tableau_de_bord?username={username}", status_code=303)

    

