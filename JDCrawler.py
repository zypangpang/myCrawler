from time import sleep
import requests
import json
from functools import partial
from bs4 import BeautifulSoup
from utils import url_refine
#import lxml.html

import constants

class JDCrawler:
    root_url='https://jd.com'
    search_base_url='https://search.jd.com/Search'

    jd_url=partial(url_refine,base_url=root_url)

    '''
    # Parsing html with lxml directly example
    def __parse_lxml(self,html):
        html=lxml.html.fromstring(html)
        items=html.cssselect(".gl-i-wrap")
        commodities=[]
        for item in items:
            extracted_item = {}
            extracted_item['img'] = self.jd_url(item.cssselect('img')[0].get('data-lazy-img'))
            extracted_item['name'] = item.cssselect('.p-name em')[0].text_content()
            extracted_item['url'] = self.jd_url(item.cssselect('a')[0].get('href'))
            extracted_item['price'] = item.cssselect('.p-price')[0].text_content().strip()
            commodities.append(extracted_item)
        print(commodities)
    '''

    def __parse_search_item(self,html):
        soup = BeautifulSoup(html, 'lxml')
        commodity_items=soup.select(".gl-i-wrap")
        print(commodity_items[0])
        commodities=[]
        for item in commodity_items:
            extracted_item={}
            extracted_item['img']=self.jd_url(item.select_one('img')['data-lazy-img'])
            extracted_item['name']=item.select_one('.p-name em').text
            extracted_item['url']=url=self.jd_url(item.select_one('a')['href'])
            extracted_item['id'] = int(url[url.rfind('/')+1:-5])
            extracted_item['price']=item.select_one('.p-price').text.strip()
            extracted_item['comment']=item.select_one('.p-commit').text.strip()
            commodities.append(extracted_item)
        return commodities


    def search(self, keyword, page=1):
        url=self.search_base_url
        params={
            'keyword':keyword,
            'page':page
        }
        headers = {'user-agent': constants.USER_AGENT}
        r=requests.get(url,params=params,headers=headers)
        #self.__parse_search_item(r.text)
        return self.__parse_search_item(r.text)

    def get_comment_number(self,item_ids,referer):
        comment_url = 'https://club.jd.com/comment/productCommentSummaries.action'
        #?my=pinglun&referenceIds=&callback=jQuery9252258&_='
        params = {
            'my': 'pinglun',
            'referenceIds': ','.join([str(x) for x in item_ids]),
            'callback': 'jQuery9252258',
            #'_': 1618021862044,
            # 'isShadowSku':0,
            # 'fold':1
        }
        headers = {
            'user-agent': constants.USER_AGENT,
            'referer': referer
        }
        r = requests.get(comment_url, params=params, headers=headers)
        j = json.loads(r.text[14:-2])
        keys=['ProductId','CommentCountStr','GoodCountStr','PoorCountStr']
        return [
            dict(zip(keys,[item[key] for key in keys]))
            for item in j['CommentsCount']
        ]

    def __parse_comments(self,id,score,page,only_text=True):
        comment_url = 'https://club.jd.com/comment/productPageComments.action'
        # 'callback=fetchJSON_comment98&productId=67973435803&score=2&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'
        params = {
            'callback': 'fetchJSON_comment',
            'productId': id,
            'score': score,
            'sortType': 5,
            'page': page,
            'pageSize': 10,
            # 'isShadowSku':0,
            # 'fold':1
        }
        headers = {
            'user-agent': constants.USER_AGENT,
            'referer': 'https://www.jd.com'
        }
        r = requests.get(comment_url, params=params, headers=headers)
        j=json.loads(r.text[18:-2])
        if only_text:
            comments=[
                {
                    'id':item['id'],
                    'content':item['content'],
                    'score': item['score']
                }
                for item in j['comments']
            ]
        else:
            comments=j['comments']
        return comments

    def get_commodity_comments(self,id,score=0,number=10):
        '''
        获取评论信息
        :param url: 商品详情页地址
        :param score: 好评：3, 中评：2, 差评：1, 全部评论：0
        :return:
        '''
        #id=int(url[url.rfind('/')+1:-5])
        comments=[]
        page=0
        while len(comments) < number:
            print(f"get page {page} ...")
            new_comments=self.__parse_comments(id,score,page)
            if not new_comments:
                break
            comments+=new_comments
            page+=1
            sleep(1)
        return comments


if __name__ == '__main__':
    jd_crawler=JDCrawler()
    #jd_crawler.search("红酒")
    cmts=jd_crawler.get_commodity_comments(67973435803,score=1,number=10)
    print(cmts)
    #cmt_counts=jd_crawler.get_comment_number([67155415602,27339475626],'https://www.jd.com')
    #print(cmt_counts)

