import os
import requests
import urllib3


def download_file(file_url, payload, file_path):
    response = requests.get(file_url, params=payload, verify=False)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)


def main():
    urllib3.disable_warnings()
    book_url = 'https://tululu.org/txt.php'
    folder = 'books'
    os.makedirs(folder, exist_ok=True)
    for id in range(1, 11):
        payload = {"id": id}
        file_name = f'id{id}.txt'
        file_path = os.path.join(os.getcwd(), folder, file_name)
        download_file(book_url, payload, file_path)


if __name__ == '__main__':
    main()
