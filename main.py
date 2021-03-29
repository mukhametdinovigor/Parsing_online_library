import argparse
import json
import os
from urllib.parse import urljoin, urlparse, unquote

from environs import Env
import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from pathvalidate.argparse import sanitize_filepath_arg


def get_book_pages_count():
    url = 'https://tululu.org/l55/'
    books_page = get_scifi_books_page_html(url)
    soup = BeautifulSoup(books_page, 'lxml')
    pages_count_selector = '.npage'
    pages_count = int(soup.select(pages_count_selector)[-1].text)
    return pages_count


def create_args_parser(pages_count):
    env = Env()
    env.read_env()
    dest_folder = env('DEST_FOLDER')
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_page', default=1, type=int)
    parser.add_argument('-e', '--end_page', default=pages_count, type=int)
    parser.add_argument('-d', '--dest_folder', default=dest_folder, type=sanitize_filepath_arg)
    parser.add_argument('-si', '--skip_imgs', action='store_true', default=False)
    parser.add_argument('-st', '--skip_txt', action='store_true', default=False)
    args = parser.parse_args()
    return args


def check_for_errors(response):
    response.raise_for_status()
    if len(response.history):
        raise requests.HTTPError()


def get_scifi_books_page_html(url):
    response = requests.get(url, verify=False)
    check_for_errors(response)
    return response.text


def get_book_ids(books_page):
    soup = BeautifulSoup(books_page, 'lxml')
    id_selector = '.d_book a[href^="/b"][title^="Бесплатная"]'
    books_ids = [''.join(symbol for symbol in book_block.attrs.get('href') if symbol.isdigit()) for book_block in soup.select(id_selector)]
    return books_ids


def get_book_page_html(book_id, payload):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url, params=payload, verify=False)
    check_for_errors(response)
    return response.text


def parse_book_page(book_description):
    soup = BeautifulSoup(book_description, 'lxml')
    title_author_selector = 'h1'
    image_selector = '.bookimage img'
    comments_selector = '.texts .black'
    genres_selector = 'span.d_book a'
    book_title, book_author = soup.select(title_author_selector)[0].text.split('::')
    image_name = soup.select(image_selector)[0].attrs.get('src')
    image_url = urljoin('https://tululu.org', image_name)
    book_comments = [comment.text for comment in soup.select(comments_selector)]
    book_genres = [genre.text for genre in soup.select(genres_selector)]
    book_attributes = {
        'book_title': book_title.strip(),
        'book_author': book_author.strip(),
        'image_url': image_url,
        'book_comments': book_comments,
        'book_genres': book_genres
    }
    return book_attributes


def download_file(filename, folder, response_file, mode):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, sanitize_filename(filename))
    with open(file_path, mode, encoding='utf-8') as file:
        file.write(response_file)
    return file_path


def download_book(filename, folder, response):
    book_path = download_file(filename, folder, response.text, 'w')
    return book_path


def download_cover(image_url, filename, folder):
    response = requests.get(image_url, verify=False)
    check_for_errors(response)
    os.makedirs(folder, exist_ok=True)
    image_path = os.path.join(folder, sanitize_filename(filename))
    with open(image_path, 'wb') as file:
        file.write(response.content)
    return image_path


def get_book_path(skip_txt, txt_file_name, books_folder_path, response):
    if skip_txt:
        book_path = ''
        return book_path
    book_path = download_book(txt_file_name, books_folder_path, response)
    return book_path


def get_img_src(skip_imgs, image_url, image_file_name, images_folder_path):
    if skip_imgs:
        img_src = ''
        return img_src
    img_src = download_cover(image_url, image_file_name, images_folder_path)
    return img_src


def get_books_json(book_attributes, img_src, book_path, book_json_path):
    books = {
        'title': book_attributes.get('book_title'),
        'author': book_attributes.get('book_author'),
        'img_src': img_src,
        'book_path': book_path,
        'comments': book_attributes.get('book_comments'),
        'genres': book_attributes.get('book_genres')
    }
    with open(book_json_path, 'a', encoding='utf8') as my_file:
        json.dump(books, my_file, ensure_ascii=False, indent=4)


def main():
    urllib3.disable_warnings()
    pages_count = get_book_pages_count()
    print(f'На сайте страниц книг - {pages_count}.')
    args = create_args_parser(pages_count)
    scifi_books_url = 'https://tululu.org/l55/'
    book_url = 'https://tululu.org/txt.php'
    books_folder_path = os.path.join(args.dest_folder, 'books')
    images_folder_path = os.path.join(args.dest_folder, 'images')
    book_json_path = os.path.join(args.dest_folder, 'books.json')
    for page_number in range(args.start_page, args.end_page + 1):
        scifi_books_page_url = urljoin(scifi_books_url, str(page_number))
        books_page = get_scifi_books_page_html(scifi_books_page_url)
        book_ids = get_book_ids(books_page)
        for book_id in book_ids:
            payload = {"id": book_id}
            try:
                response = requests.get(book_url, params=payload, verify=False)
                check_for_errors(response)
                book_description = get_book_page_html(book_id, payload)
                book_attributes = parse_book_page(book_description)
                book_title = book_attributes.get('book_title')
                image_url = book_attributes.get('image_url')
                txt_file_name = f'{book_id}.{book_title}.txt'
                image_file_name = unquote(os.path.split(urlparse(image_url).path)[1])
                book_path = get_book_path(args.skip_txt, txt_file_name, books_folder_path, response)
                img_src = get_img_src(args.skip_imgs, image_url, image_file_name, images_folder_path)
                get_books_json(book_attributes, img_src, book_path, book_json_path)
            except requests.exceptions.HTTPError:
                continue


if __name__ == '__main__':
    main()
