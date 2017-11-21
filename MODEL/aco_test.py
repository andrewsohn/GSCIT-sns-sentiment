from __future__ import print_function
from konlpy.tag import Kkma, Twitter
from konlpy import jvm
import nltk
import json
import csv
import os
import glob
import settings
import argparse
import re
import pants
import math
import random
import datetime
from konlpy.utils import pprint

def main():
    #   Arguments  #
    parser = argparse.ArgumentParser(description='Pengtai Instagram RNN LSTM Model')
    parser.add_argument('-t', '--type', type=str, help="run type Options: 'n' for new | 'o' for overwrite", default='o',
                        nargs='+')
    # parser.add_argument('-d', '--dest_dir', type=str, help='CSV data file')
    parser.add_argument('-i', '--input_dir', type=str, help='Input Raw CSV directory')
    parser.add_argument('-u', '--user_id', type=str, help='Instagram User ID')
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

    with open('./dic/polarity.csv', 'r', encoding='UTF-8') as file:
        csvreader = csv.DictReader(file)
        kosac = [row for row in csvreader]

    total_arr = []
    rowI = 0
    rowDict = {}

    # File List in the directory from the arguments
    for filename in glob.glob(os.path.join(args.input_dir, '*.csv')):
        # i = ['id', 'img', 'text', 'has_tag', 'write_date', 'reg_date']
        with open(filename, 'r', encoding='UTF-8') as f:
            csvreader = csv.DictReader(f)
            # csvreader = csv.reader(f)
            for row in csvreader:
                if rowI == 0:
                    rowDict = {
                        "user_id": row['user_id'],
                        "posts": []
                    }
                else:
                    # print(user_id, row['user_id'], rowDict)
                    if rowDict['user_id'] != row['user_id']:
                        total_arr.append(rowDict)
                        rowDict = {
                            "user_id": row['user_id'],
                            "posts": []
                        }

                # text preprocess
                text = re.sub(r'@\w+', '', row['text'])
                text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '',
                              text)
                text = re.sub(r'[\[]|[\]]', '', text)
                text = re.sub(r'[\r]|[\n]', ' ', text)
                text = re.sub(r'[.]|[ㆍ]', '', text)
                text = re.sub(r'#', ' ', text)

                rowDict['posts'].append({"datetime": row['write_date'], "text": text})
                rowI = rowI + 1

    # print(total_arr)
    trg_res = [item for item in total_arr if item["user_id"] == args.user_id]
    temp = []
    kkma = Kkma()
    t = Twitter()

    for post in trg_res[0]['posts']:
        date = datetime.datetime(int(post['datetime'][0:4]), int(post['datetime'][5:7]), int(post['datetime'][8:10]),
                                 int(post['datetime'][11:13]), int(post['datetime'][14:16]),
                                 int(post['datetime'][17:19]))
        text = post['text']
        temp.append((date, text))

    temp = sorted(temp, key=lambda t: t[0], reverse=False)


    sentArr = []
    newArr = []
    tokens_ko = []
    index = 0
    nounsArr = []

    for data in temp:
        sentPosArr = kkma.pos(data[1])
        # sentNouns = kkma.nouns(data[1])

        inArr = []
        for outA in sentPosArr:
            # for inA in outA:
            inArr.append("/".join(outA))

        morph_arr = t.morphs(data[1])
        morphWords = [word for word in morph_arr if not word in tokens_ko]
        for word in morphWords:
            if not word in nounsArr:
                nounsArr.append(word)

        tokens_ko.extend(morphWords)

        newArr.append({"sentence": "", "words":morph_arr, "score": 0})

        index = index + 1
        sentArr.append(";".join(inArr))

    index = 0
    for eaSent in sentArr:
        sentiScore = 0
        for corp in kosac:
            if eaSent.find(corp['ngram']) > -1:
                if corp['max.value'] == 'NEG':
                    sentiScore = sentiScore - float(corp['max.prop'])
                elif corp['max.value'] == 'POS':
                    sentiScore = sentiScore + float(corp['max.prop'])

        newArr[index]["sentence"] = eaSent
        newArr[index]["score"] = sentiScore

        index = index+1

    # ACO 알고리즘

    # doc_ko = " ".join([row[1] for row in temp])
    # text_arr = [row[1] for row in temp]
    # for text in text_arr:
    #     morph_arr = t.morphs(text)
    #     temp = [word for word in morph_arr if not word in tokens_ko]
    #     tokens_ko.extend(temp)

    print(tokens_ko)
    ko = nltk.Text(tokens_ko)  # For Python 2, input `name` as u'유니코드'

    # # print(len(set(ko.tokens)))  # returns number of unique tokens
    vocab = dict([(item[0], index + 1) for index, item in enumerate(ko.vocab().items())])
    # pprint(vocab)  # returns number of tokens (document length)
    minTimeVal = int(temp[0][0].timestamp())
    maxTimeVal = int(temp[len(temp)-1][0].timestamp() - minTimeVal)

    tenPow = len(str(int(temp[len(temp)-1][0].timestamp() - minTimeVal)))
    tenPow = pow(10, tenPow)

    index = 0
    nodes = []

    for data in temp:
        # print(data[0].utctimetuple)
        # print(data[0].time())
        diffTimeVal = int(data[0].timestamp() - minTimeVal)

        opt1 = float(diffTimeVal / tenPow)
        opt2 = float(diffTimeVal / maxTimeVal)
        print(diffTimeVal, opt1, opt2)

        nodes.append((opt2,newArr[index]["words"]))
        index = index + 1

    # print(nounsArr)
    nodes2 = []
    for noun in nounsArr:
        for corp in kosac:
            hts = "%s/NNG" % (noun)
            if hts.find(corp['ngram']) > -1:
                if corp['max.value'] == 'NEG':
                    nodes2.append({"noun":noun, "score":-float(corp['max.prop'])})
                elif corp['max.value'] == 'POS':
                    nodes2.append({"noun": noun, "score": float(corp['max.prop'])})

    print()
    antCount = len(newArr)
    rhoVal = 0.3
    # ACO 알고리즘 예시
    # nodes = []
    # for _ in range(20):
    #     x = random.uniform(-10, 10)
    #     y = random.uniform(-10, 10)
    #     nodes.append((x, y))
    #
    def euclidean(a, b):
        return math.sqrt(pow(a[1] - b[1], 2) + pow(a[0] - b[0], 2))
    #
    world = pants.World (nodes, euclidean)
    #
    solver = pants.Solver(rho=rhoVal, )
    #
    # solution = solver.solve(world)
    # solutions = solver.solutions(world)
    #
    # print(solution.distance)
    # print(solution.tour)  # Nodes visited in order
    # print(solution.path)  # Edges taken in order
    #
    # best = float("inf")
    # for solution in solutions:
    #     assert solution.distance < best
    #     best = solution.distance
    #
    # print(best)


if __name__ == "__main__":
    jvm.init_jvm()
    main()