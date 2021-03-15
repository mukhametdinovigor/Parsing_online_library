import argparse
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
    book_comments = []
    comments = soup.find_all('div', class_='texts')
    for comment in comments:
        book_comments.append(comment.contents[4].text)
    genres = soup.find('span', class_='d_book').find_all('a')
    book_genres = []
    for genre in genres:
        book_genres.append(*genre.contents)
    book_attributes = {
        'book_title': book_title,
        'book_author': book_author,
        'image_url': image_url,
        'book_comments': book_comments,
        'book_genres': book_genres
    }
    return book_attributes


def check_for_redirect(book_url, payload):
    response = requests.get(book_url, params=payload, verify=False)
    if len(response.history):
        raise requests.HTTPError()


def download_file(filename, folder, response_content):
    os.makedirs(folder, exist_ok=True)
    file_path = sanitize_filepath(os.path.join(folder, sanitize_filename(filename)))
    with open(file_path, 'wb') as file:
        file.write(response_content)


def download_book(filename, folder, book_url, payload):
    response = requests.get(book_url, params=payload, verify=False)
    response.raise_for_status()
    download_file(filename, folder, response.content)


def download_cover(image_url, filename, folder):
    response = requests.get(image_url, verify=False)
    response.raise_for_status()
    download_file(filename, folder, response.content)


def main():
    urllib3.disable_warnings()
    args = create_args_parser()
    book_url = 'https://tululu.org/txt.php'
    book_folder = 'books'
    images_folder = 'images'
    for book_id in range(args.start_id, args.end_id + 1):
        payload = {"id": book_id}
        try:
            check_for_redirect(book_url, payload)
        except requests.exceptions.HTTPError:
            continue
        book_description = get_book_page_html(book_id, payload)
        book_attributes = parse_book_page(book_description)
        book_title = book_attributes.get('book_title')
        image_url = book_attributes.get('image_url')
        txt_file_name = f'{book_id}. {book_title}.txt'
        image_file_name = unquote(os.path.split(urlparse(image_url).path)[1])
        download_book(txt_file_name, book_folder, book_url, payload)
        download_cover(image_url, image_file_name, images_folder)


if __name__ == '__main__':
    main()
