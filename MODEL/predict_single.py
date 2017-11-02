from __future__ import print_function

import numpy as np
import json
import os
from konlpy.tag import Twitter
from keras.preprocessing import sequence
from keras.models import load_model
import settings
# from konlpy.utils import pprint

def main():
    with open(settings.VERSION_JSON, "r") as jsonFile:
        data = json.load(jsonFile)

    VERSION = data['version']

    with open("new_data.json", "r") as jf:
        dt = json.load(jf)

    text = dt['text']

    x_arr = []

    t = Twitter()
    vocab_fn = settings.VOCAB_FILENAME.format(VERSION)
    vocab_file = os.path.join(settings.DATA_DIR, vocab_fn)
    jobj = json.loads((open(vocab_file).read()))

    arr = list()
    tokens_ko = t.morphs(text)

    for word in tokens_ko:
        try:
            tmp = jobj[word]
            arr.append(tmp)
        except KeyError:
            pass

    temp_arr = np.asarray(arr)
    x_arr.append(temp_arr)

    x_test = np.asarray(x_arr, dtype=object)

    print('Pad sequences (samples x time)')
    x_test = sequence.pad_sequences(x_test, maxlen=settings.MAX_LENGTH)
    print('x_test shape:', x_test.shape)

    mod_load_fn = settings.MODEL_FILENAME.format(VERSION)
    mod_load_path = os.path.join(settings.OUTPUT_DIR, mod_load_fn)
    model = load_model(mod_load_path)

    classes = model.predict(x_test, batch_size=settings.BATCH_SIZE)
    print(classes)

if __name__ == "__main__":
    main()