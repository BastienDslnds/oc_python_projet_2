# Extraction des données du site Books to Scrape

Programme permettant l'extraction d'informations du site Books to Scrape

## Description

Le projet a pour but d'extraire:
- les informations de chaque livre de chaque catégorie du site
- les images de chaque livre

Les informations des livres sont les suivantes :
- product_page_url
- universal_ product_code (upc)
- title
- price_including_tax
- price_excluding_tax 
- number_available
- category
- review_rating
- image_url
- product_description

## Préparation

### Dépendances

* installer Windows, version 10.0.19043
* installer python 3.10

### Installation
* git clone https://github.com/BastienDslnds/oc_python_projet_2.git
* Créer et activer l'environnement virtuel 
  * 1- ouvrir l'application "invite de commande"
  * 2- se positionner dans le dossier "oc_python_projet_2" contenant le fichier requirements.txt
  * 3- utiliser la commande suivante: "pip install -r requirements.txt"

### Execution du programme

* Se positionner dans le dossier "oc_python_projet_2"
* Utiliser la commande "python main.py"
* Laisser tourner le script pour obtenir:
  * un dossier "fichiers_csv" avec l'ensemble des données par catégorie
  * un dossier "images_livres" avec toutes les images de livres

## Auteurs

Bastien Deslandes

bastien.deslandes@free.fr