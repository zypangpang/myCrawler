import requests

import constants


def url_refine(raw_url:str,base_url):
    if raw_url.startswith("//"):
        return 'http:'+raw_url

    if raw_url.startswith('/'):
        return base_url+raw_url

    return raw_url

def fetch_html(url,params={}):
    headers = {'user-agent': constants.USER_AGENT}
    r = requests.get(url, params=params, headers=headers)
    return r.text
