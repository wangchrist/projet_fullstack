import csv
import psycopg2
from psycopg2 import sql


def insert_data(cursor, data):
    insert_query = sql.SQL("""
        INSERT INTO evenement (
            id ,url, titre, chapeau, description, date_de_debut, date_de_fin,
            description_de_la_date, url_de_limage, mots_cles, nom_du_lieu,
            adresse_du_lieu, code_postal, ville, url_de_contact,
            telephone_de_contact, email_de_contact, type_de_prix, detail_du_prix,
            type_dacces, url_de_reservation, audience
        )
        VALUES (
            %(ID)s,%(URL)s, %(Titre)s, %(Chapeau)s, %(Description)s, %(Date de debut)s, %(Date de fin)s,
            %(Description de la date)s, %(URL de limage)s, %(Mots cles)s, %(Nom du lieu)s,
            %(Adresse du lieu)s, %(Code postal)s, %(Ville)s, %(Url de contact)s,
            %(Telephone de contact)s, %(Email de contact)s, %(Type de prix)s, %(Detail du prix)s,
            %(Type dacces)s, %(URL de reservation)s, %(audience)s
        )
        ON CONFLICT (id) DO NOTHING;
    """)
    cursor.execute(insert_query, data)

def fill_db():

    # Paramètres de connexion
    db_params = {
        'dbname': 'mydatabase',
        'user': 'myuser',
        'password': 'mypassword',
        'host':'database',
        'port': '5432',
    }

    # Connexion avec la base de données PostgreSQL
    connection = psycopg2.connect(**db_params)

    cursor = connection.cursor()
    create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS evenement (
            id INT PRIMARY KEY NOT NULL,
            url TEXT,
            titre TEXT,
            chapeau TEXT,
            description TEXT,
            date_de_debut TIMESTAMP,
            date_de_fin TIMESTAMP,
            description_de_la_date TEXT,
            url_de_limage TEXT,
            mots_cles TEXT,
            nom_du_lieu TEXT,
            adresse_du_lieu TEXT,
            code_postal TEXT,
            ville TEXT,
            url_de_contact TEXT,
            telephone_de_contact TEXT,
            email_de_contact TEXT,
            type_de_prix TEXT,
            detail_du_prix TEXT,
            type_dacces TEXT,
            url_de_reservation TEXT,
            audience TEXT
        );
    """)
    cursor.execute(create_table_query)

    create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS utilisateur (
            id SERIAL PRIMARY KEY NOT NULL,
            identifiant TEXT,
            mdp TEXT
        );
    """)
    cursor.execute(create_table_query)

    create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS liste (
            id_utilisateur INT,
            id_evenement INT,
            FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id),
            FOREIGN KEY (id_evenement) REFERENCES evenement(id)
        );
    """)
    cursor.execute(create_table_query)
    # i=0

    try:

        with open('evenement_clean.csv', 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                for key, value in row.items():
                    if key in ['Date de debut', 'Date de fin'] and not value:
                        row[key] = None
        
                insert_data(cursor, row)
                # i+=1
                # print(i)

        connection.commit()

    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        cursor.close()
        connection.close()


# fill_db()