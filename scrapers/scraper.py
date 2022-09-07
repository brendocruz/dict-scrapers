import requests
from bs4 import BeautifulSoup as Soup
import lxml
import cchardet

class Scraper():
    def __init__(self, url: str):
        self.url: str     = url
        self.timeout: int = 4
        self._source      = None
        self._scraped     = None
        self._sanitazed   = None

    def load(self):
        self._scraped = requests.Session().get(self.full_url(), headers={
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }, timeout=self.timeout)

    def raw(self):
        if not self._scraped:
            self.load()
        return self._scraped

    def html(self):
        if not self._source:
            self._source = Soup(self.raw().text, 'lxml')
        return self._source

    def extract(self):
        if not self._sanitazed:
            self._sanitized = self.html()
        return self._sanitized 

    def full_url(self) -> str:
        return self.url

