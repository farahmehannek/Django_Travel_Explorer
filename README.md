# Django Travel Explorer
# MEHANNEK FARAH

Projet de site web de gestion et d’exploration de voyages développé avec Django.

## Description  
    Django Travel Explorer permet aux utilisateurs de découvrir, planifier et gérer des voyages grâce à une interface simple. Le système inclut :  
    - Création, consultation et modification d’itinéraires de voyage.  
    - Gestion des utilisateurs avec authentification.  
    - Recherche de destinations.  
    - Tableau de bord d’administration pour les gestionnaires de voyages.

##  Stack technique  
    - Backend : [Django](https://www.djangoproject.com/) (Python)  
    - Base de données : SQLite (pour développement) / … (production)  
    - Frontend : Django Templates + HTML/CSS (+ optionnellement Bootstrap)  
    - Environnement virtuel : venv  
    - Versionnage : Git, hébergé sur GitHub

## Installation locale  
1. Cloner le dépôt :  
   ```bash
   git clone https://github.com/farahmehannek/Django_Travel_Explorer.git
   cd Django_Travel_Explorer
2. Créer et activer l’environnement virtuel :

        python3 -m venv venv
        # venv\Scripts\activate    # sur Windows
Installer les dépendances :

    pip install -r requirements.txt


Appliquer les migrations et lancer le serveur de développement :

    python manage.py migrate
    python manage.py runserver


Accéder à l’application dans le navigateur :
  
          http://127.0.0.1:8000/

Fonctionnalités principales:

    Authentification des utilisateurs (inscription, connexion, déconnexion)
    
    Création et gestion des voyages (ajout, édition, suppression)
    
    Recherche des destinations avec filtres
    
    Interface d’administration pour gérer les contributions utilisateurs
    
    Responsive design (interface utilisable sur mobile et desktop)

