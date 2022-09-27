import requests
from bs4 import BeautifulSoup
import shutil
import re
import os
import pandas as pd

# Donnée d'entrée: url du site
site_url = 'http://books.toscrape.com/catalogue/category/books_1/index.html'

# Récupérer le code html du site (EXTRACTION)
site_response = requests.get(site_url)
site_soup = BeautifulSoup(site_response.content.decode('utf-8'), 'html.parser')

# Trouver les url des catégories de livre (EXTRACTION)
categories_list = site_soup.findAll('ul')[2].findAll('a', href=True)  # liste des balises <a href="url">xxx<a/>

# Créer le dossier pour stocker les fichiers csv (CHARGEMENT)
CUR_DIR = os.path.dirname(__file__)  # récupérer le chemin du dossier dans lequel se trouve mon fichier python
CSV_DIR = os.path.join(CUR_DIR, "fichiers_csv")

if os.path.exists(CSV_DIR):
    shutil.rmtree(CSV_DIR)
os.mkdir("fichiers_csv")

# Créer le dossier pour stocker les images (CHARGEMENT)
IMAGES_DIR = os.path.join(CUR_DIR, "images_livres")

if os.path.exists(IMAGES_DIR):
    shutil.rmtree(IMAGES_DIR)
os.mkdir("images_livres")

# Boucler sur chaque catégorie pour obtenir les informations de ces livres
for category in categories_list:
    # Supprimer le saut de ligne (TRANSFORMATION)
    category_title_init = category.text.replace("\n", "")
    # Supprimer les espaces avant et après le titre (TRANSFORMATION)
    category_title = category_title_init.lstrip().rstrip()
    print(category_title)
    # Récupérer l'url de la catéogrie et supprimer les ../ (TRANSFORMATION)
    category_url_found = category['href'].replace("../", "")
    # Reformater l'url (TRANSFORMATION)
    category_url = f"http://books.toscrape.com/catalogue/category/{category_url_found}"
    # Récupérer le code HTML de la catégorie (EXTRACTION)
    category_response = requests.get(category_url)
    category_soup = BeautifulSoup(category_response.content.decode('utf-8'), 'html.parser')
    # Récupérer le nombre de pages de la catégorie (EXTRACTION)
    nb_page = category_soup.find('li', class_="current")
    if nb_page is None:  # si le champ est vide alors il n'y a qu'une seule page pour la catégorie (EXTRACTION)
        nb_page = 1
    else:
        nb_page = nb_page.text.strip()[-1:]  # récupérer le nombre de page(s) (EXTRACTION)

    # Création du dataframe de la catégorie avec les en-tête (CHARGEMENT)
    columns = ['product_page_url',
               'universal_ product_code (upc)',
               'title',
               'price_including_tax',
               'price_excluding_tax',
               'number_available',
               'category',
               'review_rating',
               'image_url',
               'product_description']

    df_category = pd.DataFrame(columns=columns)

    # Parcourir chaque page pour obtenir les informations des livres de chaque page (EXTRACTION)
    for page in range(int(nb_page)):
        if page == 0:  # pour la première page, l'url est différent donc le cas est géré avec ce if
            category_page_url = category_url
        else:
            category_page_url_modified = category_page_url.replace("index.html", "")
            category_page_url = f'{category_page_url_modified}page-{page + 1}.html'
        # Récupérer le code HTML de la page de la catégorie (EXTRACTION)
        page_response = requests.get(category_page_url)
        page_soup = BeautifulSoup(page_response.content.decode('utf-8'), 'html.parser')
        # Récupérer le nombre de livres de la page (EXTRACTION)
        nb_books_by_page = len(page_soup.findAll('h3'))
        for i in range(int(nb_books_by_page)):  # boucler sur chaque livre de la page
            # Récupérer l'URL du livre (EXTRACTION)
            book_url_found = page_soup.findAll('h3')[i].find('a')['href'].replace("../", "")

            # Formater l'URL du livre (TRANSFORMATION)
            book_url = f"http://books.toscrape.com/catalogue/{book_url_found}"

            # Récupérer le code HTML du livre (EXTRACTION)
            book_response = requests.get(book_url)
            book_soup = BeautifulSoup(book_response.content.decode('utf-8'), 'html.parser')
            print(book_soup)

            # Récupérer les informations du livre (EXTRACTION + TRANSFORMATION)
            product_page_url = book_url
            universal_product_code = book_soup.find("table", class_="table table-striped").findAll("td")[0].text
            price_including_tax_init = book_soup.find("table", class_="table table-striped").findAll("td")[3].text
            price_including_tax = price_including_tax_init.lstrip("Â£")
            price_excluding_tax_init = book_soup.find("table", class_="table table-striped").findAll("td")[2].text
            price_excluding_tax = price_excluding_tax_init.lstrip("Â£")
            number_available_initial = book_soup.find("table", class_="table table-striped").findAll("td")[5].text
            number_available = re.sub(r'\D', '', str(number_available_initial))
            title = book_soup.find("h1").text
            product_description = book_soup.findAll('p')[3].text
            category = book_soup.find('ul', class_="breadcrumb").findAll('a')[2].text
            review_rating = book_soup.findAll("p", class_="star-rating")[0]['class'][1]
            image_URL = book_soup.findAll('img')[0]['src'].replace("../..", "http://books.toscrape.com")

            # Récupérer l'image du livre (EXTRACTION)
            r_image = requests.get(image_URL).content
            # Formater le nommage du fichier de l'image (TRANSFORMATION)
            title_formated = ''.join(char for char in title if char.isalnum())
            # Stocker l'image (CHARGEMENT)
            with open(f"images_livres/{title_formated}.jpg", "wb+") as file_image:
                file_image.write(r_image)

            # Stocker les informations du livre dans un fichier csv (CHARGEMENT)
            df_category_new_row = pd.DataFrame({'product_page_url': [product_page_url],
                                                'universal_ product_code (upc)': [universal_product_code],
                                                'title': [title],
                                                'price_including_tax': [price_including_tax],
                                                'price_excluding_tax': [price_excluding_tax],
                                                'number_available': [number_available], 'category': [category],
                                                'review_rating': [review_rating], 'image_url': [image_URL],
                                                'product_description': [product_description]})
            df_category = pd.concat([df_category, df_category_new_row])
            df_category.to_csv(f"fichiers_csv/categorie_{category_title}.csv", sep='>', index=False, encoding="utf-8")