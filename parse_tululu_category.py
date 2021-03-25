import requests
import urllib3
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def get_scifi_books_page_html(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    return response.text


def get_book_ids(books_page):
    soup = BeautifulSoup(books_page, 'lxml')
    book_blocks = soup.find_all('table', class_='d_book')
    books_ids = [book_block.find('a').attrs.get('href')[2:-1] for book_block in book_blocks]
    return books_ids


def main():
    urllib3.disable_warnings()
    scifi_books_url = 'https://tululu.org/l55/'
    for page_number in range(1, 11):
        books_page_url = urljoin(scifi_books_url, str(page_number))
        books_page = get_scifi_books_page_html(books_page_url)
        book_ids = get_book_ids(books_page)
        print(*book_ids)


if __name__ == '__main__':
    main()