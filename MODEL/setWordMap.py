from __future__ import print_function
import numpy as np
from konlpy.tag import Twitter;
from konlpy.corpus import kobill  # Docs from pokr.kr/bill
from konlpy.corpus import CorpusLoader    # Docs from pokr.kr/bill
import nltk
from konlpy.utils import pprint
from konlpy import jvm
import json
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional
from keras.datasets import imdb

# (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=max_features)

def main():
    # ./data/하위 csv파일을 읽어 /Users/Andrew-MB/DEV/05.GIT/GSCIT-sns-sentiment/MODEL/env/lib/python3.6/site-packages/konlpy/data/corpus/insta
    # 하위로 txt파일을 생성해야 한다.

    vocab_path = "./data/lstm_data171101.json"
    # files_ko = kobill.fileids()  # Get file ids
    corpus = CorpusLoader('insta')

    doc_ko = corpus.open("lstm_data171101.txt").read()


    t = Twitter()
    tokens_ko = t.morphs(doc_ko)

    ko = nltk.Text(tokens_ko, name='insta')  # For Python 2, input `name` as u'유니코드'

    # pprint(ko.tokens)  # returns number of tokens (document length)
    print(len(set(ko.tokens)))  # returns number of unique tokens
    # returns frequency distribution
    # for k, v in ko.vocab().items():
    #     print(k,v)
    # i = 1
    vocab = dict([(item[0], index) for index, item in enumerate(ko.vocab().items())])

    with open(vocab_path, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(vocab))


if __name__ == "__main__":
    jvm.init_jvm()
    main()