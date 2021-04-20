import json

from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
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
    return (X_train,y_train),(X_test,y_test)

class Doc2VecHelper:
    def __init__(self):
        self.model = Doc2Vec.load("doc2vec.model")

    def train(self,X):
        documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(X)]
        model = Doc2Vec(documents, vector_size=100, window=2, min_count=1, workers=4)
        model.save("doc2vec.model")
        return model

    def fit_transform(self,X):
        if isinstance(X[0], str):
            X=[v.split() for v in X]
        if not self.model:
            self.model=self.train(X)
        return self.transform(X)

    def transform(self,X):
        if isinstance(X[0],str):
            X=[v.split() for v in X]
        #X=[res['word'] for res in word_cut.paddle_cut(X)]
        return [self.model.infer_vector(words) for words in X]



class SentimentAnalysis:
    feature_number='150'
    def __init__(self,vec_method="TW",cut_method='paddle',stop_words=()):
        '''
        构造函数
        :param vec_method: 向量化方法: TW, TC, TF, TF-IDF
        :param pos_data: list of sentences
        :param neg_data: list of sentences
        '''
        self.__vec_method=vec_method
        self.__stop_words=stop_words
        self.__cut_method=cut_method

        #if pos_data and neg_data:
        #    self.load_data(pos_data,neg_data)

    def __get_vectorizer(self):
        __vectorizer_map = {
            'TW': CountVectorizer(binary=True,stop_words=self.__stop_words),
            'TC': CountVectorizer(stop_words=self.__stop_words),
            'TF': TfidfVectorizer(use_idf=False,stop_words=self.__stop_words),
            'TF-IDF': TfidfVectorizer(use_idf=True,stop_words=self.__stop_words),
            'Doc2Vec': Doc2VecHelper()
        }
        return __vectorizer_map[self.__vec_method]

    '''
    def load_data(self,pos_data,neg_data,stop_words=()):
        self.__pos_data=pos_data
        self.__neg_data=neg_data
        self.__stop_words=stop_words
    '''


    def __word_cut(self,X):
        if self.__cut_method == 'paddle':
            results=word_cut.paddle_cut(X)
        else:
            results=word_cut.jieba_cut(X)
        return [' '.join(res['word']) for res in results]

    def __vectorize(self,X):
        X=self.__word_cut(X)
        self.__vectorizer=self.__get_vectorizer()
        return self.__vectorizer.fit_transform(X)

    def __feature_selection(self,X,y):
        X=self.__vectorize(X)
        if self.__vec_method != 'Doc2Vec':
            self.__feature_selector=SelectKBest(chi2, k=self.feature_number)
            X = self.__feature_selector.fit_transform(X, y)
        return X

    def train(self, X, y):
        X=self.__feature_selection(X,y)
        self.__clf=NuSVC(nu=0.4,kernel='rbf').fit(X,y)

    def predict(self,X):
        X=self.__vectorizer.transform(X)
        if self.__vec_method != 'Doc2Vec':
            X=self.__feature_selector.transform(X)
        return self.__clf.predict(X)


if __name__ == '__main__':
    #print(read_stop_words("data/baidu_stopwords.txt")[:10])
    pos_data=read_comment_json("data/jdcmts_good.json")
    neg_data = read_comment_json("data/jdcmts_bad.json")
    train_data,test_data=split_data(pos_data,neg_data)
    stop_words=read_stop_words("data/baidu_stopwords.txt")
    sa=SentimentAnalysis(vec_method='Doc2Vec',cut_method='paddle',stop_words=stop_words)
    sa.train(train_data[0],train_data[1])
    pred_y=sa.predict(test_data[0])
    print(accuracy_score(test_data[1],pred_y))

