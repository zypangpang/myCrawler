class SentimentAnalysis:
    def __init__(self,vec_method="TW", pos_data=None,neg_data=None):
        '''
        构造函数
        :param vec_method: 向量化方法: TW, TC, TF, TF-IDF
        :param pos_data:
        :param neg_data:
        '''
        self.vec_method=vec_method
        if pos_data and neg_data:
            self.load_data(pos_data,neg_data)

    def load_data(self,pos_data,neg_data):
        self.__pos_data=pos_data
        self.__neg_data=neg_data

    def vectorize(self):