# Online library parser

This script is for parsing online library [tululu.org](https://tululu.org) and downloading scifi books. There are 701 pages of
scifi books  on the site, 25 books on each page.
Scripts collects such data about book:
 - book title
 - book author
 - book cover
 - book comments
 - book genres
 
and write this information into book.json. It looks like this:
```
{
    "title": "Деревня Медный ковш",
    "author": "Патрацкая Наталья Владимировна",
    "img_src": ""C:\\images\\59569.jpg"",
    "book_path": "C:\\books\\59569.Деревня Медный ковш.txt",
    "comments": ["Отличная книга"],
    "genres": [
        "Научная фантастика",
        "Прочие приключения",
        "Современные любовные романы"
    ]
}
```
## How to install

Download code.
Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

## How to run script

Run script in command line:
```
python3 main.py
```

This command downloads books from page 1 to 701 to folder `books`. Book covers are downloaded to a folder
`images`. Information about books are downloaded into file `book.json`.

You can use such commandline arguments, first - short version, second - long version, you should use
one of them:

```
-s, --start_page
```

this command is needed to configure number of starting page, by default it is 1.

`main.py -s 680` - will download books from page 680 to 701.


```
-e, --end_page
```

this command is needed to configure number of ending page, by default it is 701.

`main.py --start_page 680 --end_page 687` - will download books from page 680 to 687.

```
-d, --dest_folder
```

this command is needed to configure folder for books, images and book.json, by default it is home folder of your project.

`main.py -d C:\My_books` - will download books to folder My_books (this example is for Windows).

```
-si, --skip_imgs
```

this command is needed to to skip downloading images, if you specify it in commandline like this 

`main.py -skip_imgs` images won't be downloaded.

```
-st, --skip_txt
```

this command is needed to to skip downloading books, if you specify it in commandline like this 

`main.py --skip_txt` books won't be downloaded.


## Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
