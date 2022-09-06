import requests

class Scraper():
    def __init__(self, url):
        self.url = url
        self.scraped_page = None
        self.timeout      = 4

    def _load_page(self):
        self.scraped_page = requests.Session().get(self.url, headers={
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }, timeout=self.timeout)

    def extract(self):
        self._load_page()
        return self.scraped_page.text
