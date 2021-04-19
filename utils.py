import json

import requests
from bs4 import UnicodeDammit

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
    r.encoding='utf-8'
    return r.text

def fetch_binary(url,params={}):
    headers = {'user-agent': constants.USER_AGENT}
    r = requests.get(url, params=params, headers=headers)
    return r.content


def decode_html(html_str):
    converted = UnicodeDammit(html_str)
    if not converted.unicode_markup:
        raise UnicodeDecodeError(
            "Failed to detect encoding, tried [%s]",
            ', '.join(converted.tried_encodings)
        )
    return converted.unicode_markup

def write_json(obj,file_path=None):
    json_str=json.dumps(obj, ensure_ascii=False, indent="  ")
    if file_path:
        with open(file_path,"w") as f:
            f.write(json_str)
    else:
        print(json_str)
