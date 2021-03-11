# Online library parser

This script is for parsing online library [tululu.org](https://tululu.org) and downloading books.
It collects such data about book:
 - book title
 - book author
 - book cover
 - book comments
 - book genre

### How to install

Download code.
Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

Run scripts in command line:
```
python3 main.py
```
This command downloads books with `book id` from 1 to 10 to folder `books`. Book covers are downloaded to a folder
`images`.
To download books with different ids you need to specify them in the command line:
```
python3 main.py 20 30
```
This command will download books with book id from 20 to 30.

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
