from __future__ import print_function

import argparse
import numpy as np
import json
import os
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional
from getDataSet import load_data
import settings

def main():
    #   Arguments  #
    parser = argparse.ArgumentParser(description='Pengtai Instagram RNN LSTM Model')
    parser.add_argument('-t', '--type', type=str, help="run type Options: 'n' for new | 'o' for overwrite", default='o',
                        nargs='+')
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

    max_features = 100000
    # cut texts after this number of words
    # (among top max_features most common words)
    maxlen = 100
    batch_size = 32

    print('Loading data...')

    npz_fn = settings.INPUT_DATA_FILENAME.format(VERSION)
    npz_file = os.path.join(settings.INPUT_DIR, npz_fn)
    (x_train, y_train), (x_test, y_test) = load_data(npz_file)

    print(len(x_train), 'train sequences')
    print(len(x_test), 'test sequences')

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

    mod_save_fn = settings.MODEL_FILENAME.format(VERSION)
    mod_save_path = os.path.join(settings.OUTPUT_DIR, mod_save_fn)
    model.save(mod_save_path)
    del model

if __name__ == "__main__":
    main()