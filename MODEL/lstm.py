from __future__ import print_function
import numpy as np
from konlpy.tag import Twitter;
from konlpy.corpus import kobill  # Docs from pokr.kr/bill
from konlpy.corpus import CorpusLoader    # Docs from pokr.kr/bill
import nltk
from konlpy.utils import pprint
from konlpy import jvm
import csv
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional
from keras.datasets import imdb
from getDataSet import load_data

# (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=max_features)

def main():
    max_features = 100000
    # cut texts after this number of words
    # (among top max_features most common words)
    maxlen = 100
    batch_size = 32

    print('Loading data...')
    # temp = imdb.load_data(num_words=max_features)

    (x_train, y_train), (x_test, y_test) = load_data("./data/lstm_data171101.npz")

    # (x_train, y_train), (x_test, y_test) = temp
    # print(temp)
    print(len(x_train), 'train sequences')
    print(len(x_test), 'test sequences')
    #
    print('Pad sequences (samples x time)')
    x_train = sequence.pad_sequences(x_train, maxlen=maxlen)
    x_test = sequence.pad_sequences(x_test, maxlen=maxlen)
    print('x_train shape:', x_train.shape)
    print('x_test shape:', x_test.shape)
    y_train = np.array(y_train)
    y_test = np.array(y_test)

    model = Sequential()
    model.add(Embedding(max_features, 128, input_length=maxlen))
    model.add(Bidirectional(LSTM(64)))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    # try using different optimizers and different optimizer configs
    model.compile('adam', 'binary_crossentropy', metrics=['accuracy'])

    print('Train...')
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=4,
              validation_data=[x_test, y_test])

if __name__ == "__main__":
    jvm.init_jvm()
    main()