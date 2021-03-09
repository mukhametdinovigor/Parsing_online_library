import os
from urllib.parse import urljoin, urlparse, unquote

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath


def check_for_redirect(response):
    if len(response.history):
        raise requests.HTTPError()


def download_file(filename, folder, response_content):
    os.makedirs(folder, exist_ok=True)
    file_path = sanitize_filepath(os.path.join(folder, sanitize_filename(filename)))
    with open(file_path, 'wb') as file:
        file.write(response_content)


def download_cover(image_url, filename, folder):
    response = requests.get(image_url, verify=False)
    response.raise_for_status()
    download_file(filename, folder, response.content)


def get_book_attributes(book_id, payload):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url, params=payload, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_title = soup.find('h1').text.split('::')[0].strip()
    image_name = soup.find('div', class_='bookimage').find('img').attrs.get('src')
    image_url = urljoin('https://tululu.org', image_name)
    book_comments = []
    comments = soup.find_all('div', class_='texts')
    for comment in comments:
        book_comments.append(comment.contents[4].text)
    return book_title, image_url, book_comments


def main():
    urllib3.disable_warnings()
    book_url = 'https://tululu.org/txt.php'
    book_folder = 'books'
    images_folder = 'images'
    for book_id in range(1, 11):
        payload = {"id": book_id}
        response = requests.get(book_url, params=payload, verify=False)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue
        book_title, image_url, book_comments = get_book_attributes(book_id, payload)
        txt_file_name = f'{book_id}. {book_title}.txt'
        image_file_name = unquote(os.path.split(urlparse(image_url).path)[1])
        download_file(txt_file_name, book_folder, response.content)
        download_cover(image_url, image_file_name, images_folder)
        print(book_title)
        print(*book_comments)


if __name__ == '__main__':
    main()
