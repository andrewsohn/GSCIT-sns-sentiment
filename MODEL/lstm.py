from __future__ import print_function
import numpy as np
from konlpy.tag import Twitter;
from konlpy.corpus import kobill  # Docs from pokr.kr/bill
from konlpy.corpus import CorpusLoader    # Docs from pokr.kr/bill
import nltk
from konlpy.utils import pprint
import csv
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional
from keras.datasets import imdb

# (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=max_features)

def main():
    # with open("./data/lstm_data171031.csv") as f:
    #     csvreader = csv.reader(f)
    #     exist_ids = [row for row in csvreader]

    # print(exist_ids)

    # files_ko = kobill.fileids()  # Get file ids
    # temp = CorpusLoader('insta')\
    # temp.abspath(filename="/Users/Andrew-MB/DEV/05.GIT/GSCIT-sns-sentiment/MODEL/data/lstm_data171031.csv")
    # doc_ko = temp.open("lstm_data171031.csv").read()

    files_ko = kobill.fileids()  # Get file ids
    doc_ko = kobill.open('1809890.txt').read()


    t = Twitter()
    tokens_ko = t.morphs(doc_ko)

    ko = nltk.Text(tokens_ko, name='대한민국 국회 의안 제 1809890호')  # For Python 2, input `name` as u'유니코드'

    print(len(ko.tokens))  # returns number of tokens (document length)
    print(len(set(ko.tokens)))  # returns number of unique tokens
    temp = ko.vocab()  # returns frequency distribution
    pprint(temp)

if __name__ == "__main__":
	main()