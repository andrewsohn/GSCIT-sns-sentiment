import os
VERSION_JSON = "versions.json"
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'MODEL')
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_DIR = os.path.join(BASE_DIR, 'in')
OUTPUT_DIR = os.path.join(BASE_DIR, 'out')

CSV_FILENAME = "lstm_data.{}.csv"
CORPUS_NAME = "insta"
CORPUS_FILENAME = "lstm_data.{}.txt"
VOCAB_FILENAME = "lstm_data.{}.json"
INPUT_DATA_FILENAME = "lstm_data.{}.npz"
MODEL_FILENAME = "model.{}.h5"
MODEL_WEIGHT_FILENAME = "model.weight.{}.h5"
MODEL_ARCH_FILENAME = "model.arch.{}.json"

# DATA SET
TRAIN_TEST_RATIO = 0.25
DATASET_RANTOM_STATE = 42

# MODEL
BATCH_SIZE = 32
MAX_LENGTH = 100