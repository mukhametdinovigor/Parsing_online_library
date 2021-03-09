import os
import requests
import urllib3

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath


def check_for_redirect(response):
    if len(response.history):
        raise requests.HTTPError()


def download_txt(txt_url, filename, folder, payload):
    os.makedirs(folder, exist_ok=True)
    file_path = sanitize_filepath(os.path.join(folder, sanitize_filename(filename)))
    response = requests.get(txt_url, params=payload, verify=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.exceptions.HTTPError:
        return
    with open(file_path, 'wb') as file:
        file.write(response.content)


def get_book_title(book_id, payload):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url, params=payload, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('h1').text.split('::')[0].strip()
    return title


def main():
    urllib3.disable_warnings()
    book_url = 'https://tululu.org/txt.php'
    folder = 'books'
    os.makedirs(folder, exist_ok=True)
    for book_id in range(1, 11):
        payload = {"id": book_id}
        book_title = f'{book_id}. {get_book_title(book_id, payload)}.txt'
        download_txt(book_url, book_title, folder, payload)


if __name__ == '__main__':
    main()
