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
from xml.dom.minidom import parseString
from sklearn.model_selection import train_test_split
import json
import random

def find_values(id, json_repr):
    results = []

    def _decode_dict(a_dict):
        try: results.append(a_dict[id])
        except KeyError: pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict)  # Return value ignored.
    return results

def main():
    with open("./data/lstm_data171101.csv", 'r') as f:
        csvreader = csv.reader(f)
        next(csvreader)
        csv_data = [row for row in csvreader]

    random.shuffle(csv_data)

    x_arr = []
    y_arr = []

    t = Twitter()
    jobj = json.loads((open ("./data/lstm_data171101.json").read()))

    for data in csv_data:
        arr = list()
        tokens_ko = t.morphs(data[0])
        y_arr.append(data[1])

        for word in tokens_ko:
            try:
                tmp = jobj[word]
                arr.append(tmp)
            except KeyError:
                pass

        # print(arr)
        x_arr.append(arr)

    x_train, x_test, y_train, y_test = train_test_split(x_arr, y_arr, test_size=0.5, random_state=42)

    # all_arr = {
    #     'data': {
    #         'x_train': x_train,
    #         'x_test': x_test,
    #         'y_train': y_train,
    #         'y_test': y_test
    #     }
    # }
    #
    # test = np.array(all_arr['data'])

    # np.save("./data/lstm_data171101.npz",test)
    np.savez("./data/lstm_data171101.npz", x_train=x_train, x_test=x_test,y_train=y_train,y_test=y_test)


if __name__ == "__main__":
    jvm.init_jvm()
    main()
