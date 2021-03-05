import os
import requests
import urllib3


def download_file(response, file_path):
    with open(file_path, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if len(response.history):
        raise requests.HTTPError()


def main():
    urllib3.disable_warnings()
    book_url = 'https://tululu.org/txt.php'
    folder = 'books'
    os.makedirs(folder, exist_ok=True)
    for id in range(1, 11):
        payload = {"id": id}
        file_name = f'id{id}.txt'
        file_path = os.path.join(os.getcwd(), folder, file_name)
        response = requests.get(book_url, params=payload, verify=False)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue
        download_file(response,file_path)


if __name__ == '__main__':
    main()
