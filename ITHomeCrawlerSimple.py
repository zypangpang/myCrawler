from functools import partial

import requests
import constants
from bs4 import BeautifulSoup

from utils import url_refine, fetch_html


class ITHomeCrawlerSimple:
    news_base_url="https://it.ithome.com/"
    it_url=partial(url_refine,base_url=news_base_url)

    def __parse_news_items(self,html):
        soup = BeautifulSoup(html, 'lxml')
        news_items = soup.select(".bl li")
        news_list = []
        for item in news_items:
            extracted_item={}
            extracted_item['title']=item.select_one('h2').text
            extracted_item['description']=item.select_one('.m').text.strip()
            extracted_item['url']=self.it_url(item.select_one("a")['href'])
            extracted_item['img']=self.it_url(item.select_one('img')['src'])
            extracted_item['tags']=item.select_one(".tags").text.strip()
            extracted_item['time']=item.select_one(".state").text.strip()

            news_list.append(extracted_item)

        return news_list

    def fetch_news(self,category):
        url=self.news_base_url+category
        params = {}
        headers = {'user-agent': constants.USER_AGENT}
        r = requests.get(url, params=params, headers=headers)
        # self.__parse_search_item(r.text)
        return self.__parse_news_items(r.text)


if __name__ == '__main__':
    crawler=ITHomeCrawlerSimple()
    list=crawler.fetch_news("")
    print(list[3])

