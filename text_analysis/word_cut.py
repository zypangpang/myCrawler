from collections import defaultdict

import jieba
import paddlehub as hub


def jieba_cut(text_list):
    results=[]
    for text in text_list:
        seg_list = jieba.cut(text, cut_all=False)
        results.append( { 'word':list(seg_list) } )
    return results


def paddle_cut(text_list,tag=False):
    lac = hub.Module(name="lac")
    results = lac.cut(text=text_list, use_gpu=False, batch_size=1, return_tag=tag)
    return results

def word_count(text_list):
    wc=defaultdict(int)
    for words in text_list:
        for word in words:
            wc[word]+=1
    return wc

if __name__ == '__main__':
    text=["今天是个好天气"]
    print(jieba_cut(text))