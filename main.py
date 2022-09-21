import requests
from bs4 import BeautifulSoup
import re
import os

# Donnée d'entrée: url du site
url_site = 'http://books.toscrape.com/catalogue/category/books_1/index.html'

# Récupérer le code html du site (EXTRACTION)
response_site = requests.get(url_site)
soup_site = BeautifulSoup(response_site.text, 'html.parser')

# Trouver les url des catégories de livre (EXTRACTION)
liste_categories = soup_site.findAll('ul')[2].findAll('a', href=True)  # liste des balises <a href="url">xxx<a/>

# Créer le dossier pour stocker les fichiers csv (CHARGEMENT)
os.mkdir("fichiers_csv")

# Créer le dossier pour stocker les images (CHARGEMENT)
os.mkdir("images_livres")

# Boucler sur chaque catégorie pour obtenir les informations de ces livres
for categorie in liste_categories:
    # Supprimer le saut de ligne (TRANSFORMATION)
    categorie_titre_init = categorie.text.replace("\n", "")
    # Supprimer les espaces avant et après le titre (TRANSFORMATION)
    categorie_titre = categorie_titre_init.lstrip().rstrip()
    # Récupérer l'url de la catéogrie et supprimer les ../ (TRANSFORMATION)
    url_category_found = categorie['href'].replace("../", "")
    # Reformater l'url (TRANSFORMATION)
    url_category = f"http://books.toscrape.com/catalogue/category/{url_category_found}"
    # Récupérer le code HTML de la catégorie (EXTRACTION)
    response_category = requests.get(url_category)
    soup_category = BeautifulSoup(response_category.text, 'html.parser')
    # Récupérer le nombre de pages de la catégorie (EXTRACTION)
    nb_page = soup_category.find('li', class_="current")
    if nb_page is None:  # si le champ est vide alors il n'y a qu'une seule page pour la catégorie (EXTRACTION)
        nb_page = 1
    else:
        nb_page = nb_page.text.strip()[-1:]  # récupérer le nombre de page(s) (EXTRACTION)
    # Parcourir chaque page pour obtenir les informations des livres de chaque page (EXTRACTION)
    for page in range(int(nb_page)):
        if page == 0:  # pour la première page, l'url est différent donc le cas est géré avec ce if
            url_category_page = url_category
        else:
            url_category_page_modified = url_category_page.replace("index.html", "")
            url_category_page = f'{url_category_page_modified}page-{page + 1}.html'
        # Récupérer le code HTML de la page de la catégorie (EXTRACTION)
        response_page = requests.get(url_category_page)
        soup_page = BeautifulSoup(response_page.text, 'html.parser')
        # Récupérer le nombre de livres de la page (EXTRACTION)
        nb_livres_page = len(soup_page.findAll('h3'))
        for i in range(int(nb_livres_page)):  # boucler sur chaque livre de la page
            # Récupérer l'URL du livre (EXTRACTION)
            url_livre_found = soup_page.findAll('h3')[i].find('a')['href'].replace("../", "")

            # Formater l'URL du livre (TRANSFORMATION)
            url_livre = f"http://books.toscrape.com/catalogue/{url_livre_found}"

            # Récupérer le code HTML du livre (EXTRACTION)
            response_livre = requests.get(url_livre)
            soup_livre = BeautifulSoup(response_livre.text, 'html.parser')

            # Récupérer les informations du livre (EXTRACTION + TRANSFORMATION)
            product_page_url = url_livre
            universal_product_code = soup_livre.find("table", class_="table table-striped").findAll("td")[0].text
            price_including_tax = soup_livre.find("table", class_="table table-striped").findAll("td")[3].text.lstrip("Â")
            print(price_including_tax)
            price_excluding_tax = soup_livre.find("table", class_="table table-striped").findAll("td")[2].text.lstrip("Â")
            number_available_initial = soup_livre.find("table", class_="table table-striped").findAll("td")[5].text
            number_available = re.sub(r'\D', '', str(number_available_initial))
            title = soup_livre.find("h1").text
            product_description = soup_livre.findAll('p')[3].text
            category = soup_livre.find('ul', class_="breadcrumb").findAll('a')[2].text
            review_rating = soup_livre.findAll("p", class_="star-rating")[0]['class'][1]
            image_URL = soup_livre.findAll('img')[0]['src'].replace("../..", "http://books.toscrape.com")

            # Récupérer l'image du livre (EXTRACTION)
            r = requests.get(image_URL).content
            # Formater le nommage du fichier de l'image (TRANSFORMATION)
            title_formated = ''.join(char for char in title if char.isalnum())
            # Stocker l'image (CHARGEMENT)
            with open(f"images_livres/{title_formated}.jpg", "wb+") as file_image:
                file_image.write(r)

            # Stocker les informations du livre dans un fichier csv (CHARGEMENT)
            with open(f'fichiers_csv/categorie_{categorie_titre}.csv', 'a', encoding="utf-8") as file:
                file.write(
                    'product_page_url>universal_ product_code (upc)>title>price_including_tax>price_excluding_tax>number_available>category>review_rating>image_url>product_description\n')
                file.write(
                    f"{product_page_url}>{universal_product_code}>{title}>{price_including_tax}>{price_excluding_tax}>{number_available}>{category}>{review_rating}>{image_URL}>{product_description}")