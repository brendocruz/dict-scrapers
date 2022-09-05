import requests

requests_session = requests.Session()

def load_page(url, timeout=4):
    res = requests_session.get(url, headers={
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
    }, timeout=timeout)
    return res
