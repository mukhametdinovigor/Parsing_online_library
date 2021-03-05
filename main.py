import requests
import urllib3

from urllib.parse import urlparse


book_url = 'https://tululu.org/txt.php?id=32168'
urllib3.disable_warnings()
file_name = f'{urlparse(book_url).query.replace("=", "")}.txt'

response = requests.get(book_url, verify=False)
response.raise_for_status()
with open(file_name, 'wb') as file:
    file.write(response.content)
