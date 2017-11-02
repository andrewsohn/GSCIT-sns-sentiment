from __future__ import print_function
from konlpy.tag import Twitter;
from konlpy.corpus import CorpusLoader
from konlpy.utils import installpath as konlpy_path
import nltk
from konlpy import jvm
import json
import csv
import os
import settings
import argparse

def main():
    #   Arguments  #
    parser = argparse.ArgumentParser(description='Pengtai Instagram RNN LSTM Model')
    parser.add_argument('-t', '--type', type=str, help="run type Options: 'n' for new | 'o' for overwrite", default='o',
                        nargs='+')
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

    # ./data/하위 csv파일을 읽어 /Users/Andrew-MB/DEV/05.GIT/GSCIT-sns-sentiment/MODEL/env/lib/python3.6/site-packages/konlpy/data/corpus/insta
    # 하위로 txt파일을 생성해야 한다.

    name = settings.CORPUS_NAME

    corpus_fn = settings.CORPUS_FILENAME.format(VERSION)
    desTxtPath = '%s/data/corpus/%s/%s' % (konlpy_path, name, corpus_fn)
    thefile = open(desTxtPath, 'w')

    with open(args.data_file, 'r') as f:
        csvreader = csv.reader(f)
        next(csvreader)
        # csv_text_data = []
        for row in csvreader:
            thefile.write("%s\n" % row[0])

    thefile.close()
    corpus = CorpusLoader(name)

    filename = settings.CORPUS_FILENAME.format(VERSION)
    doc_ko = corpus.open(filename).read()

    t = Twitter()
    tokens_ko = t.morphs(doc_ko)

    ko = nltk.Text(tokens_ko, name=name)  # For Python 2, input `name` as u'유니코드'

    # pprint(ko.tokens)  # returns number of tokens (document length)
    # print(len(set(ko.tokens)))  # returns number of unique tokens
    vocab = dict([(item[0], index) for index, item in enumerate(ko.vocab().items())])

    vocab_fn = settings.VOCAB_FILENAME.format(VERSION)
    vocab_file = os.path.join(settings.DATA_DIR, vocab_fn)

    with open(vocab_file, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(vocab))

if __name__ == "__main__":
    jvm.init_jvm()
    main()