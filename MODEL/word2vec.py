from __future__ import print_function

import argparse
import numpy as np
from konlpy.tag import Twitter
from konlpy import jvm
import csv
from sklearn.model_selection import train_test_split
import json
import random
import os
import settings

def find_values(id, json_repr):
    results = []

    def _decode_dict(a_dict):
        try: results.append(a_dict[id])
        except KeyError: pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict)  # Return value ignored.
    return results

def main():
    #   Arguments  #
    parser = argparse.ArgumentParser(description='Pengtai Instagram RNN LSTM Model')
    parser.add_argument('-t', '--type', type=str, help="run type Options: 'n' for new | 'o' for overwrite", default='o', nargs='+')
    parser.add_argument('-d', '--data_file', type=str, help='CSV data file')
    parser.add_argument('-v', '--version', help='current version', action='store_true')

    args = parser.parse_args()
    #  End Argparse #

    # VERSION CONTROL #
    if args.version:
        with open(settings.VERSION_JSON, "r") as jsonFile:
            data = json.load(jsonFile)

        return print(data['version'])

    if args.type:
        if args.type[0] == 'n' and args.type[1]:
            with open(settings.VERSION_JSON, "r") as jsonFile:
                data = json.load(jsonFile)

            data["version"] = args.type[1]

            with open(settings.VERSION_JSON, "w") as jsonFile:
                json.dump(data, jsonFile)

            VERSION = args.type[1]

        elif args.type[0] == 'o':
            with open(settings.VERSION_JSON, "r") as jsonFile:
                data = json.load(jsonFile)

            VERSION = data["version"]

    # End VERSION CONTROL #

    with open(args.data_file, 'r') as f:
        csvreader = csv.reader(f)
        next(csvreader)
        csv_data = [row for row in csvreader]

    random.shuffle(csv_data)

    x_arr = []
    y_arr = []

    t = Twitter()
    vocab_fn = settings.VOCAB_FILENAME.format(VERSION)
    vocab_file = os.path.join(settings.DATA_DIR, vocab_fn)
    jobj = json.loads((open(vocab_file).read()))

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

        x_arr.append(arr)

    x_train, x_test, y_train, y_test = train_test_split(x_arr, y_arr, test_size=settings.TRAIN_TEST_RATIO, random_state=settings.DATASET_RANTOM_STATE)

    npz_fn = settings.INPUT_DATA_FILENAME.format(VERSION)
    npz_file = os.path.join(settings.INPUT_DIR, npz_fn)
    np.savez(npz_file, x_train=x_train, x_test=x_test,y_train=y_train,y_test=y_test)

if __name__ == "__main__":
    jvm.init_jvm()
    main()
