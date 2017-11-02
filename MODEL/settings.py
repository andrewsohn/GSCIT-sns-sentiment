import os
VERSION_JSON = "versions.json"
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'MODEL')
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_DIR = os.path.join(BASE_DIR, 'in')
OUTPUT_DIR = os.path.join(BASE_DIR, 'out')

CORPUS_NAME = "insta"
CORPUS_FILENAME = "lstm_data.{}.txt"
VOCAB_FILENAME = "lstm_data.{}.json"
INPUT_DATA_FILENAME = "lstm_data.{}.npz"
MODEL_FILENAME = "model.{}.h5"

TRAIN_TEST_RATIO = 0.5
DATASET_RANTOM_STATE = 42