import requests


def recognize(path: str, api_key: str):
    files = {'file': open(path, 'rb')}
    data = {'api_token': api_key}
    r = requests.post('https://api.audd.io/', data=data, files=files)
    if r.status_code == 200:
        result = r.json().get('result')
        if result:
            return result.get('artist'), result.get('title')
    return None, None
