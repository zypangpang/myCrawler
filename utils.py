def url_refine(raw_url:str,base_url):
    if raw_url.startswith("//"):
        return 'http:'+raw_url

    if raw_url.startswith('/'):
        return base_url+raw_url