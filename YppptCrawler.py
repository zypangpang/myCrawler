from functools import partial

import lxml.html
from utils import fetch_html,url_refine,fetch_binary

class YppptCrawler:
    base_url="https://www.ypppt.com"
    yp_url=partial(url_refine,base_url=base_url)

    def get_ppt_list(self,cat="",page=1):
        if page > 1:
            page_str=f"/list-{page}.html"
        else:
            page_str="/"

        url=self.base_url+'/moban/'+cat+page_str
        html=fetch_html(url)

        doc=lxml.html.fromstring(html)
        ul=doc.cssselect("ul.posts")[0]
        items=[
            {
                'name': x.text,
                'url': self.yp_url(x.get("href")),
                'id': x.get("href")[x.get("href").rfind("/")+1:-5]
            }
            for x in ul.xpath("li/a[2]")
        ]
        return items

    def get_down_url(self,item):
        id=item['id']
        url=self.base_url+'/p/d.php?aid='+id
        doc=lxml.html.fromstring(fetch_html(url))
        ul=doc.cssselect("ul.down")[0]
        down_urls=ul.xpath("li/a/@href")
        item['down_url']=[self.yp_url(x) for x in down_urls]

    def download_file(self,path,url):
        b=fetch_binary(url)
        with open(path,'wb') as file:
            file.write(b)

if __name__ == '__main__':
    c=YppptCrawler()
    # max page: 143
    sum=0
    failed_items=[]
    for i in range(14,51):
        print(f"get ppt list in page {i}...")
        items=c.get_ppt_list("",i)
        for item in items:
            print(f"get download urls of {item['name']} ...")
            try:
                c.get_down_url(item)
                print(f"download ppt {item['name']} in page {i}...")
                c.download_file(f"ppts/{item['name']}.zip",item['down_url'][0])
            except:
                print(f"!!! download failed: {item['url']}")
                failed_items.append(item)
            #else:
            #    print(f"download finished")
        sum+=len(items)
    print(f"done! Totally downloaded {sum} ppts")
    print("failed items:")
    print(failed_items)
    print(f"failed item count: {len(failed_items)}")



