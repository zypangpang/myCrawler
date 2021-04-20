from gensim.models.doc2vec import TaggedDocument, Doc2Vec
from gensim.test.utils import common_texts
from gensim.models import Word2Vec
from text_analysis.sentiment_analysis import read_comment_json,split_data
from text_analysis import word_cut


pos_data=read_comment_json("data/jdcmts_good.json")
neg_data = read_comment_json("data/jdcmts_bad.json")
train_data,test_data=split_data(pos_data,neg_data)

def train():
    X=train_data[0]
    y=train_data[1]
    X=[res['word'] for res in word_cut.paddle_cut(X)]

    documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(X)]
    model = Doc2Vec(documents,dm=1, vector_size=100, window=5, min_count=5, workers=4,epochs=10)

    model.save("doc2vec.model")

def transform():
    X_test=test_data[0]
    X_test=[res['word'] for res in word_cut.paddle_cut(X_test)]
    model = Doc2Vec.load("doc2vec.model")
    print(model.infer_vector(X_test[0]))

if __name__ == '__main__':
    #print(common_texts)
    train()
    #transform()