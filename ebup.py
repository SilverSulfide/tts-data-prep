import ebooklib
from ebooklib import epub

import html2text

book = epub.read_epub('filelist/book.epub')

with open("filelist/est_book.txt", 'w', encoding='utf-8') as out_f:
    for image in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        decoded = image.content.decode()
        out_f.write(html2text.html2text(decoded))