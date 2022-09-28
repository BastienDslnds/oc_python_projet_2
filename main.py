import requests
from bs4 import BeautifulSoup
import shutil
import re
import os
import pandas as pd


CUR_DIR = os.path.dirname(__file__)  # get project file path
CSV_DIR = os.path.join(CUR_DIR, "fichiers_csv")
IMG_DIR = os.path.join(CUR_DIR, "images_livres")


def extract_categories_url(categories_list):
    """Extract url of each category."""

    urls_found = []
    for category in categories_list:
        urls_found.append(category['href'])
    return urls_found


def extract_books_url(books_page):
    """Extract url of each book of a books page."""

    books_urls_found = []
    for book in books_page:
        books_urls_found.append(book.find('a')['href'])
    return books_urls_found


def extract_books_url_category(pages_urls):
    """Get url of each book of a category by reading through each category's page."""

    books_urls_category = []
    for page_url in pages_urls:
        print(page_url)
        page_response = requests.get(page_url)
        page_soup = BeautifulSoup(page_response.content.decode('utf-8'), 'html.parser')
        books_list = page_soup.findAll('h3')

        books_urls_found = extract_books_url(books_list)
        books_urls = transform_books_url(books_urls_found)
        for book_url in books_urls:
            books_urls_category.append(book_url)

    return books_urls_category


def extract_categories_title(categories_list):
    """Extract each category title."""

    titles_categories_found = []
    for element in categories_list:
        titles_categories_found.append(element.text)
    return titles_categories_found


def extract_books_data_category(books_category_url):
    """Extract books information from a category by reading through a list of books url."""

    product_page_urls = []
    universal_product_codes = []
    titles = []
    prices_including_tax = []
    prices_excluding_tax = []
    categories = []
    reviews_ratings = []
    numbers_availables = []
    image_urls = []
    product_descriptions = []
    for book_url in books_category_url:
        book_response = requests.get(book_url)
        # parse the HTML in BeautifulSoup objects
        book_soup = BeautifulSoup(book_response.content.decode('utf-8'), 'html.parser')

        product_page_urls.append(book_url)

        universal_product_code_found = book_soup.find("table", class_="table table-striped").findAll("td")[0].text
        universal_product_codes.append(universal_product_code_found)

        title = book_soup.find("h1").text
        titles.append(title)

        price_including_tax_found = book_soup.find("table", class_="table table-striped").findAll("td")[3].text
        prices_including_tax.append(price_including_tax_found.lstrip("Â£"))

        price_excluding_tax_found = book_soup.find("table", class_="table table-striped").findAll("td")[3].text
        prices_excluding_tax.append(price_excluding_tax_found.lstrip("Â£"))

        category = book_soup.find('ul', class_="breadcrumb").findAll('a')[2].text
        categories.append(category)

        review_rating = book_soup.findAll("p", class_="star-rating")[0]['class'][1]
        reviews_ratings.append(review_rating)

        number_available_found = book_soup.find("table", class_="table table-striped").findAll("td")[5].text
        numbers_availables.append(re.sub(r'\D', '', str(number_available_found)))

        image_url_found = book_soup.findAll('img')[0]['src'].replace("../..", "http://books.toscrape.com")
        image_urls.append(image_url_found)

        product_description = book_soup.findAll('p')[3].text
        product_descriptions.append(product_description)

    return product_page_urls, \
        universal_product_codes, \
        titles, \
        prices_including_tax, \
        prices_excluding_tax, \
        categories, \
        reviews_ratings, \
        numbers_availables, \
        image_urls, \
        product_descriptions


def transform_categories_url(categories_url_found):
    """Transform categories url."""

    urls = []
    for url in categories_url_found:
        url_found_modified = url.replace("../", "")
        url_new = f"http://books.toscrape.com/catalogue/category/{url_found_modified}"
        urls.append(url_new)
    return urls


def transform_books_url(books_url_found):
    """Transform books url."""

    books_urls = []
    for url in books_url_found:
        url_found_modified = url.replace("../", "")
        url_new = f"http://books.toscrape.com/catalogue/{url_found_modified}"
        books_urls.append(url_new)
    return books_urls


def transform_categories_title(categories_title):
    """Transform categories title."""

    titles = []
    for title in categories_title:
        title_modified = title.replace("\n", "").lstrip().rstrip()
        titles.append(title_modified)
    return titles


def load_books_data_categories(categories_titles, books_data_categories):
    """Load books information from each category. """

    if os.path.exists(CSV_DIR):
        shutil.rmtree(CSV_DIR)
    os.mkdir("fichiers_csv")

    for category_title, books_data_category in zip(categories_titles, books_data_categories):
        df_category = pd.DataFrame({'product_page_url': books_data_category[0],
                                    'universal_ product_code (upc)': books_data_category[1],
                                    'title': books_data_category[2],
                                    'price_including_tax': books_data_category[3],
                                    'price_excluding_tax': books_data_category[4],
                                    'number_available': books_data_category[5],
                                    'category': books_data_category[6],
                                    'review_rating': books_data_category[7],
                                    'image_url': books_data_category[8],
                                    'product_description': books_data_category[9]})
        df_category.to_csv(f"fichiers_csv/categorie_{category_title}.csv", sep='>', index=False, encoding="utf-8-sig")


def load_books_image(books_data_category):
    """Load books image. """

    for image_url, title in zip(books_data_category[8], books_data_category[2]):
        r_image = requests.get(image_url).content
        title_formated = ''.join(char for char in title if char.isalnum())
        with open(f"images_livres/{title_formated}.jpg", "wb+") as file_image:
            file_image.write(r_image)


def get_pages_url_of_category(category_url, nb_pages):
    """Get url of each page in the category."""
    pages_urls = []
    for page in range(int(nb_pages)):
        if page == 0:  # pour la première page, l'url est différent donc le cas est géré avec ce if
            pages_urls.append(category_url)
        else:
            page_url_modified = category_url.replace("index.html", "")
            page_url = f'{page_url_modified}page-{page + 1}.html'
            pages_urls.append(page_url)
    return pages_urls


def etl():
    # if a file for images already exists, remove it
    if os.path.exists(IMG_DIR):
        shutil.rmtree(IMG_DIR)
    os.mkdir("images_livres")

    # link page to scrap
    site_url = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
    site_response = requests.get(site_url)

    # parse the HTML in BeautifulSoup object
    site_soup = BeautifulSoup(site_response.content.decode('utf-8'), 'html.parser')
    categories_list = site_soup.findAll('ul')[2].findAll('a', href=True)

    # extract categories url
    categories_url = extract_categories_url(categories_list)

    # transform categories urls
    categories_url = transform_categories_url(categories_url)

    # extract categories title
    categories_title = extract_categories_title(categories_list)

    # transform categories title
    categories_title = transform_categories_title(categories_title)

    # create a folder storing books information of each category
    books_data_categories = []

    for category_url in categories_url:
        category_response = requests.get(category_url)
        category_soup = BeautifulSoup(category_response.content.decode('utf-8'), 'html.parser')

        # get page(s) number of the category
        nb_pages = category_soup.find('li', class_="current")
        if nb_pages is None:  # if field is empty, there is only one page for the category
            nb_pages = 1
        else:
            nb_pages = nb_pages.text.strip()[-1:]

        pages_url_of_category = get_pages_url_of_category(category_url, nb_pages)
        books_url_category = extract_books_url_category(pages_url_of_category)
        books_data_category = extract_books_data_category(books_url_category)
        '''load_books_image(books_data_category)'''

        # store books information of the category
        books_data_categories.append(books_data_category)

    load_books_data_categories(categories_title, books_data_categories)


etl()
