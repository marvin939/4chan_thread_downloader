from bs4 import BeautifulSoup

HTML_DOC = "(177) _d_ - _d_ickfucking - Hentai_Alternative - 4chan.htm"
PRETTIFIED_FILENAME = "prettified.html"
soup = None

with open(HTML_DOC) as file:
    soup = BeautifulSoup(file, "lxml")
    with open(PRETTIFIED_FILENAME, "w") as pret:
        pret.write(soup.prettify())

