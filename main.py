import requests
from bs4 import BeautifulSoup
import shutil
import re
import os
import pandas as pd


CUR_DIR = os.path.dirname(__file__)  # get project file path
CSV_DIR = os.path.join(CUR_DIR, "fichiers_csv")
IMG_DIR = os.path.join(CUR_DIR, "images_livres")


def extract_categories_data(site_url):
    """Extract title and url of each category."""

    site_response = requests.get(site_url)
    # parse the HTML in BeautifulSoup object
    site_soup = BeautifulSoup(site_response.content.decode('utf-8'), 'html.parser')
    categories_list = site_soup.findAll('ul')[2].findAll('a', href=True)

    urls_found = []
    titles_categories_found = []
    for category in categories_list:
        urls_found.append(category['href'])
        titles_categories_found.append(category.text)
    return {'urls':  urls_found, 'titles': titles_categories_found}


def extract_books_url_category(category_url):
    """Get url of each book of a category by reading through each category's page."""

    pages_url_category = [category_url]
    page_response = requests.get(category_url)
    page_soup = BeautifulSoup(page_response.content.decode('utf-8'), 'html.parser')

    # input datas in case of multiples pages
    page_url_modified = category_url.replace("index.html", "")
    page_number = 2

    while True:
        next_page = page_soup.find('li', class_="next")
        if next_page is None:
            break
        else:
            page_url = f'{page_url_modified}page-{page_number}.html'
            pages_url_category.append(page_url)

            page_response = requests.get(page_url)
            page_soup = BeautifulSoup(page_response.content.decode('utf-8'), 'html.parser')
            page_number += 1

    books_url_category = []
    for page_url in pages_url_category:
        page_response = requests.get(page_url)
        page_soup = BeautifulSoup(page_response.content.decode('utf-8'), 'html.parser')
        books_page = page_soup.findAll('h3')

        books_url_found = extract_books_url(books_page)
        books_url = transform_books_url(books_url_found)

        for book_url in books_url:
            books_url_category.append(book_url)

    return books_url_category


def extract_books_data_category(books_url_category):
    """Extract books information from a category by reading through a list of books url."""

    product_page_urls = []
    universal_product_codes = []
    titles = []
    prices_including_tax = []
    prices_excluding_tax = []
    categories = []
    reviews_ratings = []
    numbers_availables = []
    images_urls = []
    products_descriptions = []
    for book_url in books_url_category:
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
        images_urls.append(image_url_found)

        product_description = book_soup.findAll('p')[3]
        product_description_modified = product_description.text.replace(";", ",").replace("\n", "")
        products_descriptions.append(product_description_modified)

    keys = ['product_page_urls',
            'universal_product_codes',
            'titles',
            'prices_including_tax',
            'prices_excluding_tax',
            'numbers_availables',
            'categories',
            'reviews_ratings',
            'images_urls',
            'products_descriptions']

    values = [product_page_urls,
              universal_product_codes,
              titles,
              prices_including_tax,
              prices_excluding_tax,
              categories,
              reviews_ratings,
              numbers_availables,
              images_urls,
              products_descriptions]

    books_data_category = {keys[i]: values[i] for i in range(len(keys))}

    return books_data_category


def extract_books_url(books_page):
    """Extract url of each book of a books page."""

    books_urls_found = []
    for book in books_page:
        books_urls_found.append(book.find('a')['href'])
    return books_urls_found


def transform_categories_data(categories_data):
    """Transform categories url and title."""

    urls = []
    titles = []
    for url, title in zip(categories_data['urls'], categories_data['titles']):
        url_found_modified = url.replace("../", "")
        url_new = f"http://books.toscrape.com/catalogue/category/{url_found_modified}"
        urls.append(url_new)
        title_modified = title.replace("\n", "").lstrip().rstrip()
        titles.append(title_modified)
    return {'urls': urls, 'titles': titles}


def transform_books_url(books_url_found):
    """Transform books url."""

    books_urls = []
    for url in books_url_found:
        url_found_modified = url.replace("../", "")
        url_new = f"http://books.toscrape.com/catalogue/{url_found_modified}"
        books_urls.append(url_new)
    return books_urls


def load_books_data_categories(categories_data, books_data_categories):
    """Load books information from each category. """

    if os.path.exists(CSV_DIR):
        shutil.rmtree(CSV_DIR)
    os.mkdir("fichiers_csv")

    for category_title, books_data_category in zip(categories_data['titles'], books_data_categories):
        df_category = pd.DataFrame({'product_page_url': books_data_category['product_page_urls'],
                                    'universal_ product_code (upc)': books_data_category['universal_product_codes'],
                                    'title': books_data_category['titles'],
                                    'price_including_tax': books_data_category['prices_including_tax'],
                                    'price_excluding_tax': books_data_category['prices_excluding_tax'],
                                    'number_available': books_data_category['numbers_availables'],
                                    'category': books_data_category['categories'],
                                    'review_rating': books_data_category['reviews_ratings'],
                                    'image_url': books_data_category['images_urls'],
                                    'product_description': books_data_category['products_descriptions']})
        df_category.to_csv(f"fichiers_csv/categorie_{category_title}.csv", sep=';', index=False, encoding="utf-8-sig")


def load_books_image(books_data_categories):
    """Load books image. """

    # if a file for images already exists, remove it
    if os.path.exists(IMG_DIR):
        shutil.rmtree(IMG_DIR)
    os.mkdir("images_livres")

    for books_data_category in books_data_categories:
        for image_url, title in zip(books_data_category['images_urls'], books_data_category['titles']):
            r_image = requests.get(image_url).content
            title_formated = ''.join(char for char in title if char.isalnum())
            with open(f"images_livres/{title_formated}.jpg", "wb+") as file_image:
                file_image.write(r_image)


def etl():
    site_url = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
    # extract categories data
    categories_data = extract_categories_data(site_url)

    # transform categories urls
    categories_data = transform_categories_data(categories_data)

    # create a folder storing books information of each category
    books_data_categories = []

    for category_url in categories_data['urls']:
        books_url_category = extract_books_url_category(category_url)
        books_data_category = extract_books_data_category(books_url_category)

        # store books information of the category
        books_data_categories.append(books_data_category)

    load_books_data_categories(categories_data, books_data_categories)
    load_books_image(books_data_categories)


etl()
