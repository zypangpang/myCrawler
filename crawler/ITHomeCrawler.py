from functools import partial

import lxml.html
import requests
import constants
from bs4 import BeautifulSoup

from utils import url_refine, fetch_html


class ITHomeCrawler:
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

    def get_news_content(self,news_item):
        html=fetch_html(news_item['url'])
        soup=BeautifulSoup(html,'lxml')
        news_item['content']=soup.select_one("#paragraph").text


    def fetch_news(self,category):
        url=self.news_base_url+category
        params = {}
        headers = {'user-agent': constants.USER_AGENT}
        r = requests.get(url, params=params, headers=headers)
        # self.__parse_search_item(r.text)
        return self.__parse_news_items(r.text)

    def fetch_comments(self,url):
        hash=self.__prepare_comments(url)
        html=self.__get_comments_html(hash)
        comments=self.__parse_comments_html(html)
        return comments

    def __prepare_comments(self,url):
        html=fetch_html(url)

        soup = BeautifulSoup(html, 'lxml')
        pid = soup.select_one('#ifcomment')['data']
        url = 'https://cmt.ithome.com/comment/' + pid
        html=fetch_html(url)

        soup = BeautifulSoup(html, 'lxml')
        script = soup.select_one('#commentlist script').string
        hash = script[-18:-2]
        return hash

    def __get_comments_html(self, hash):
        if not hash:
            return ""
        params = {
            'hash': hash,
            'pid': 1,
            'order': 'false',
        }
        #data = parse.urlencode(params).encode()
        url = 'https://cmt.ithome.com/webapi/getcomment'
        headers = {'user-agent': constants.USER_AGENT}
        r = requests.post(url, data=params, headers=headers)
        return r.text

    '''
    def parse_comment_html(self,html):
        etree=lxml.html.fromstring(html)
        comments = []
        entrys = etree.cssselect('li.entry')
        for entry in entrys:
            c = {
                'nickname': entry.cssselect('.nick')[0].text_content(),
                'time': entry.cssselect('.posandtime')[0].text_content(),
                'content': entry.cssselect('.comm')[0].text_content()
            }
            nested_comments = entry.cssselect('li.gh')
            if nested_comments:
                c['nested_comments'] = []
                for item in nested_comments:
                    c['nested_comments'].append({
                        'nickname': item.cssselect('.nick')[0].text,
                        'time': item.cssselect('.posandtime')[0].text,
                        'content': item.cssselect('.re_comm p')[0].text,
                    })
            comments.append(c)
        return comments
    '''

    # with open('./t.htm') as f:
    #    html=f.read()
    def __parse_comments_html(self,html):
        soup = BeautifulSoup(html, 'lxml')
        comments = []
        entrys = soup.select('li.entry')
        for entry in entrys:
            c = {'nickname': entry.select_one('.nick').text,
                 'time': entry.select_one('.posandtime').text,
                 'content': entry.select_one('.comm').text}
            nested_comments = entry.select('li.gh')
            if nested_comments:
                c['nested_comments'] = []
                for item in nested_comments:
                    c['nested_comments'].append({
                        'nickname': item.select_one('.nick').text,
                        'time': item.select_one('.posandtime').text,
                        'content': item.select_one('.re_comm p').text,
                    })
            comments.append(c)

        # Fix nested comments error caused by the wrong html
        rn = 0
        for item in reversed(comments):
            if item.get('nested_comments'):
                if rn > 0:
                    item['nested_comments'] = item['nested_comments'][:-rn]
                rn += len(item['nested_comments'])
        return comments
        # print(json.dumps(comments,ensure_ascii=False,indent=4))


if __name__ == '__main__':
    crawler=ITHomeCrawler()
    list=crawler.fetch_news("")
    print(list[3])
    crawler.get_news_content(list[3])
    #print(crawler.fetch_comments(list[3]['url']))

