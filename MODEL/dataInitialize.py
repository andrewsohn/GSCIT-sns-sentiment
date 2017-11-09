from __future__ import print_function
from konlpy.tag import Twitter;
from konlpy.corpus import CorpusLoader
from konlpy.utils import installpath as konlpy_path
import nltk
from konlpy import jvm
import json
import csv
import os
import glob
import settings
import argparse
import re

def main():
    #   Arguments  #
    parser = argparse.ArgumentParser(description='Pengtai Instagram RNN LSTM Model')
    parser.add_argument('-t', '--type', type=str, help="run type Options: 'n' for new | 'o' for overwrite", default='o',
                        nargs='+')
    parser.add_argument('-d', '--dest_dir', type=str, help='CSV data file')
    parser.add_argument('-i', '--input_dir', type=str, help='Input Raw CSV directory')
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

    total_arr = []
    happy_cnt = 0
    sad_cnt = 0
    joyful_cnt = 0
    anger_cnt = 0
    depressed_cnt = 0

    # File List in the directory from the arguments
    for filename in glob.glob(os.path.join(args.input_dir, '*.csv')):
        # i = ['id', 'img', 'text', 'has_tag', 'write_date', 'reg_date']
        with open(filename, 'r', encoding='UTF-8') as f:
            csvreader=csv.DictReader(f)
            # csvreader = csv.reader(f)
            for row in csvreader:

                # sentiment vector 0 and 1
                # 2017.11.09 0/1 to multi class
                # if row['has_tag'] == "우울" or row['has_tag'] == "화남" or row['has_tag'] == "슬픔":
                #     if row['has_tag'] == "우울":
                #         depressed_cnt = depressed_cnt+1
                #     elif row['has_tag'] == "화남":
                #         anger_cnt = anger_cnt+1
                #     elif row['has_tag'] == "슬픔":
                #         sad_cnt = sad_cnt+1
                #
                #     hash_tag_val = 0
                # else :
                #     if row['has_tag'] == "기쁨":
                #         happy_cnt = happy_cnt+1
                #     elif row['has_tag'] == "즐거움":
                #         joyful_cnt = joyful_cnt+1
                #
                #     hash_tag_val = 1
                if row['has_tag'] == "우울" or row['has_tag'] == "화남" or row['has_tag'] == "슬픔":
                    if row['has_tag'] == "우울":
                        hash_tag_val = 2
                        depressed_cnt = depressed_cnt+1
                    elif row['has_tag'] == "화남":
                        anger_cnt = anger_cnt+1
                        hash_tag_val = 4
                    elif row['has_tag'] == "슬픔":
                        sad_cnt = sad_cnt+1
                        hash_tag_val = 3
                else :
                    if row['has_tag'] == "기쁨":
                        happy_cnt = happy_cnt+1
                        hash_tag_val = 0
                    elif row['has_tag'] == "즐거움":
                        joyful_cnt = joyful_cnt+1
                        hash_tag_val = 1

                # text preprocess
                text = re.sub(r'@\w+', '', row['text'])
                text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
                text = re.sub(r'[\[]|[\]]', '', text)
                text = re.sub(r'[\r]|[\n]', ' ', text)
                text = re.sub(r'[.]|[ㆍ]', '', text)
                text = re.sub(r'#', ' ', text)


                total_arr.append([text.strip(),hash_tag_val])


    # removing duplicated data
    seen = set()
    seen_add = seen.add
    total_arr = [x for x in total_arr if not (x[0] in seen or seen_add(x[0]))]

    print('TOTAL DATA : ',len(total_arr))
    print('#기쁨 DATA : ', happy_cnt)
    print('#슬픔 DATA : ', sad_cnt)
    print('#즐거움 DATA : ', joyful_cnt)
    print('#화남 DATA : ', anger_cnt)
    print('#우울 DATA : ', depressed_cnt)

    dest_filename = settings.CSV_FILENAME.format(VERSION)
    dest_file = os.path.join(args.dest_dir, dest_filename)

    if not os.path.exists(dest_file):
        with open(dest_file, 'w', encoding='UTF-8') as f:
            f.writelines("text,class\n")

    with open(dest_file, 'a', encoding='UTF-8') as f:
        csvwrite = csv.writer(f, delimiter=',')

        for textrow in total_arr:
            csvwrite.writerow(textrow)

if __name__ == "__main__":
    jvm.init_jvm()
    main()