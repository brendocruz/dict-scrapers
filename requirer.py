import requests

class Scraper():
    def __init__(self, base_url=None, url_id=None):
        self.base_url     = '' if base_url is None else base_url
        self.url          = '' if url_id is None else url_id 
        self.scraped_page = None
        self.timeout      = 4

    def _full_url(self):
        return f'{self.base_url}{self.url}'

    def _load_page(self):
        self.scraped_page = requests.Session().get(self._full_url(), headers={
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }, timeout=self.timeout)

    def extract(self):
        self._load_page()
        return self.scraped_page.text
