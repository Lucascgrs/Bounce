# -*- coding: utf-8 -*-
import requests
import os

# Créer le dossier pour enregistrer les drapeaux
os.makedirs("flags", exist_ok=True)

# Récupération des données via l'API REST Countries
url = "https://restcountries.com/v3.1/all"
response = requests.get(url)
countries = response.json()

# Télécharger chaque drapeau au format PNG
for country in countries:
    try:
        name = country['name']['common']
        flag_url = country['flags']['png']
        flag_data = requests.get(flag_url).content

        # Nettoyage du nom du fichier
        filename = f"flags/{name.replace('/', '_')}.png"

        with open(filename, 'wb') as f:
            f.write(flag_data)
        print(f"Téléchargé : {filename}")
    except Exception as e:
        print(f"Erreur pour {country.get('name', {}).get('common', 'Inconnu')} : {e}")
