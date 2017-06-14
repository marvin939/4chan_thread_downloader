import urllib.request
from bs4 import BeautifulSoup

# url = "http://python.org"
url = "http://boards.4chan.org/g/thread/60892882"
user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Geckp/20100101 Firefox/53.0"
headers = {"User-Agent": user_agent}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as response:
    html = response.read().decode("utf-8")
    with open("dl.html", "w") as fp:
        fp.write(html)

with open("dl.html") as fp:
    soup = BeautifulSoup(fp, "lxml")

print(soup.prettify())

# Tests:
if "python" in soup.title.get_text().lower():
    print("Yep, this is python HTML website")
else:
    print("Website title:", soup.title.get_text())
