import requests

class Scraper():
    def __init__(self, url: str):
        self.url: str     = url
        self.timeout: int = 4

    def load(self):
        self.scraped_page = requests.Session().get(self.full_url(), headers={
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }, timeout=self.timeout)

    def raw(self):
        return self.scraped_page

    def extract(self):
        self.load()
        return self.raw().text

    def full_url(self) -> str:
        return self.url

scraper = Scraper('http://www.google.com')
scraper.load()
print(scraper.extract())
