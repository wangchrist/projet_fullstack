import pandas as pd
import numpy as np

def clean_data():

    df = pd.read_csv("evenement.csv", sep=";")

    colnames = ["ID", "URL", "Titre", "Chapeau", "Description", "Date de début", "Date de fin", "Description de la date", "URL de l'image", 
                "Mots clés", "Nom du lieu", "Adresse du lieu", "Code postal", "Ville", "Url de contact", "Téléphone de contact", 
                "Email de contact", "Type de prix", "Détail du prix", "Type d'accès", "URL de réservation", "audience"]

    df = df[colnames]

    new_df = df.rename(columns={"Date de début": "Date de debut", "URL de l'image": "URL de limage", "Mots clés": "Mots cles", "Téléphone de contact": "Telephone de contact", 
              "Détail du prix": "Detail du prix", "Type d'accès": "Type dacces", "URL de réservation": "URL de reservation"})
    
    new_df= new_df.fillna(np.nan)
    new_df.to_csv('evenement_clean.csv', index=False)

# clean_data()