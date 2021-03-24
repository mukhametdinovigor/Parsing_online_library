import argparse
import json
import os
from urllib.parse import urljoin, urlparse, unquote

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath


def create_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', nargs='?', default=1, type=int)
    parser.add_argument('end_id', nargs='?', default=10, type=int)
    args = parser.parse_args()
    return args


def check_for_error(book_url, payload):
    response = requests.get(book_url, params=payload, verify=False)
    response.raise_for_status()
    if len(response.history):
        raise requests.HTTPError()


def get_scifi_books_page_html(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    return response.text


def get_book_ids(books_page):
    soup = BeautifulSoup(books_page, 'lxml')
    book_blocks = soup.find_all('table', class_='d_book')
    books_ids = [book_block.find('a').attrs.get('href')[2:-1] for book_block in book_blocks]
    return books_ids


def get_book_page_html(book_id, payload):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url, params=payload, verify=False)
    response.raise_for_status()
    return response.text


def parse_book_page(book_description):
    soup = BeautifulSoup(book_description, 'lxml')
    book_title = soup.find('h1').text.split('::')[0].strip()
    book_author = soup.find('h1').text.split('::')[1].strip()
    image_name = soup.find('div', class_='bookimage').find('img').attrs.get('src')
    image_url = urljoin('https://tululu.org', image_name)
    comments = soup.find_all('div', class_='texts')
    book_comments = [comment.contents[4].text for comment in comments]
    genres = soup.find('span', class_='d_book').find_all('a')
    book_genres = [genre.text for genre in genres]
    book_attributes = {
        'book_title': book_title,
        'book_author': book_author,
        'image_url': image_url,
        'book_comments': book_comments,
        'book_genres': book_genres
    }
    return book_attributes


def download_file(filename, folder, response_file, mode):
    os.makedirs(folder, exist_ok=True)
    file_path = sanitize_filepath(os.path.join(folder, sanitize_filename(filename)))
    with open(file_path, mode) as file:
        file.write(response_file)
    return file_path


def download_book(filename, folder, book_url, payload):
    response = requests.get(book_url, params=payload, verify=False)
    response.raise_for_status()
    book_path = download_file(filename, folder, response.text, 'w')
    return book_path

def download_cover(image_url, filename, folder):
    response = requests.get(image_url, verify=False)
    response.raise_for_status()
    img_src = download_file(filename, folder, response.content, 'wb')
    return img_src

def get_books_json(book_attributes, img_src, book_path):
    books = {
        'title': book_attributes.get('book_title'),
        'author': book_attributes.get('book_author'),
        'img_src': img_src,
        'book_path': book_path,
        'comments': book_attributes.get('book_comments'),
        'genres': book_attributes.get('book_genres')
    }
    with open("books.json", "a", encoding='utf8') as my_file:
        json.dump(books, my_file, ensure_ascii=False, indent=4)



def main():
    urllib3.disable_warnings()
    args = create_args_parser()
    scifi_books_url = 'https://tululu.org/l55/'
    book_url = 'https://tululu.org/txt.php'
    book_folder = 'books'
    images_folder = 'images'
    for page_number in range(1, 5):
        scifi_books_page_url = urljoin(scifi_books_url, str(page_number))
        books_page = get_scifi_books_page_html(scifi_books_page_url)
        book_ids = get_book_ids(books_page)
        for book_id in book_ids:
            payload = {"id": book_id}
            try:
                check_for_error(book_url, payload)
                book_description = get_book_page_html(book_id, payload)
                book_attributes = parse_book_page(book_description)
                book_title = book_attributes.get('book_title')
                image_url = book_attributes.get('image_url')
                txt_file_name = f'{book_id}.{book_title}.txt'
                image_file_name = unquote(os.path.split(urlparse(image_url).path)[1])
                book_path = download_book(txt_file_name, book_folder, book_url, payload)
                img_src = download_cover(image_url, image_file_name, images_folder)
                get_books_json(book_attributes, img_src, book_path)
            except requests.exceptions.HTTPError:
                continue


if __name__ == '__main__':
    main()
