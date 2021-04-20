import json
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.svm import SVC, LinearSVC,  NuSVC
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

from text_analysis import word_cut


def read_comment_json(path,number=None):
    with open(path,"r") as f:
        cmts=json.load(f)
    if number:
        return [cmt['content'] for cmt in cmts[:number]]
    return [cmt['content'] for cmt in cmts]


def read_stop_words(path):
    with open(path,"r") as f:
        words=[w.strip() for w in f.readlines()]
    return words

def split_data(pos_data,neg_data):
    X=pos_data+neg_data
    y=[True]*len(pos_data)+[False]*len(neg_data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=33)
    return X_train,y_train,X_test,y_test

def word_split(X,cut_method='paddle'):
    if cut_method == 'paddle':
        results = word_cut.paddle_cut(X)
    else:
        results = word_cut.jieba_cut(X)
    return [res['word'] for res in results]


class SentimentAnalysis:
    #feature_number=400
    feature_number=100
    def __init__(self,vec_method="TW",stop_words=()):
        '''
        构造函数
        :param vec_method: 向量化方法: TW, TC, TF, TF-IDF
        :param pos_data: list of sentences
        :param neg_data: list of sentences
        '''
        self.__vec_method=vec_method
        self.__stop_words=stop_words
        #self.__cut_method=cut_method

        #if pos_data and neg_data:
        #    self.load_data(pos_data,neg_data)

    def __get_vectorizer(self):
        __vectorizer_map = {
            'TW': CountVectorizer(binary=True,stop_words=self.__stop_words),
            'TC': CountVectorizer(stop_words=self.__stop_words),
            'TF': TfidfVectorizer(use_idf=False,stop_words=self.__stop_words),
            'TF-IDF': TfidfVectorizer(use_idf=True,stop_words=self.__stop_words),
        }
        return __vectorizer_map[self.__vec_method]

    '''
    def load_data(self,pos_data,neg_data,stop_words=()):
        self.__pos_data=pos_data
        self.__neg_data=neg_data
        self.__stop_words=stop_words
    '''


    def __vectorize(self,X):
        X=[' '.join(words) for words in X]
        self.__vectorizer=self.__get_vectorizer()
        return self.__vectorizer.fit_transform(X)

    def __feature_selection(self,X,y):
        X=self.__vectorize(X)
        self.__feature_selector=SelectKBest(chi2, k=self.feature_number)
        X= self.__feature_selector.fit_transform(X, y)
        return X

    def train(self, X, y):
        X=self.__feature_selection(X,y)
        self.__clf=NuSVC(nu=0.4,kernel='rbf').fit(X,y)

    def predict(self,X):
        X=[' '.join(words) for words in X]
        X=self.__vectorizer.transform(X)
        X=self.__feature_selector.transform(X)
        return self.__clf.predict(X)


if __name__ == '__main__':
    #print(read_stop_words("data/baidu_stopwords.txt")[:10])
    pos_data=read_comment_json("data/jdcmts_good.json")
    neg_data = read_comment_json("data/jdcmts_bad.json")
    X_train,y_train,X_test,y_test=split_data(pos_data,neg_data)
    stop_words=read_stop_words("data/baidu_stopwords.txt")
    X_train=word_split(X_train)
    X_test=word_split(X_test)
    #print(word_cut.word_count(X_train[:10]))
    sa=SentimentAnalysis(vec_method='TW',stop_words=stop_words)
    sa.train(X_train,y_train)
    pred_y=sa.predict(X_test)
    print(accuracy_score(y_test,pred_y))

