from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from rest_framework import viewsets, status
from app.serializers import UserSerializer, GroupSerializer, AnalyzerSerializer, InstaSerializer
from django.shortcuts import render
from django.views import View
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
import datetime
from django.conf import settings
import numpy as np
import os
import json
from konlpy.tag import Kkma, Twitter
from keras.preprocessing import sequence
from keras import backend as K
from subprocess import call
from .models import SentAnalyzer, Instagram
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from django.db.utils import IntegrityError

from bs4 import BeautifulSoup
import re

try:
    from urlparse import urljoin
    from urllib import urlretrieve
except ImportError:
    from urllib.parse import urljoin, quote
    from urllib.request import urlretrieve

from .mlLoad import *
global model, graph
#initialize these variables
model, graph = init()

CSS_EXPLORE = "a[href='/explore/']"

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

# def (request):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#
#     return render(request, 'index.html', {'form': form})

# class MainView(View):
#     authentication_classes = (SessionAuthentication, BasicAuthentication)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         if not request.session.session_key:
#             return HttpResponseRedirect('/admin/')
#         # print(request.auth)

#         form = SentAnalyzerForm()
#         return render(request, 'index.html', {'form': form})

# def csv_len(fname):
#     with open(fname) as f:
#         csvreader = csv.reader(f)
#
#         row_count = sum(1 for row in csvreader)
#
#     return row_count

class AnalyzeView(APIView):
	parser_classes = (JSONParser,)
	authentication_classes = (SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		# print(request.user)

		analyz = SentAnalyzer.objects.all()
		serializer = AnalyzerSerializer(analyz, many=True)
		return Response(serializer.data)

class AnalyzePredictView(APIView):
	parser_classes = (JSONParser,)
	authentication_classes = (SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAuthenticated,)

	def initializeC(self, query, number):

		# self._driver = webdriver.Firefox()
		self._driver = webdriver.PhantomJS(settings.PHANTOMJS_PATH)

		self._driver.implicitly_wait(10)

		self.query = query
		self.accountIdx = 0
		self.totalNum = number
		self.browse_target_page()
		self.resultArr = []

		try:
			self.scrape_tags_aco(number)
		except TimeoutException:
			# print("Quitting driver...")
			self.quit()
			self.preprocess()
			return self.resultArr2

		# print("Quitting driver...")
		self.quit()
		self.preprocess()
		return self.resultArr2

	def preprocess(self):
		"""
            ACO용 전처리 작업
        """
		kkma = Kkma()
		t = Twitter()
		newArr = []
		sentArr = []
		nounsArr = []
		tokens_ko = []
		index = 0

		self.resultArr = sorted(self.resultArr, key=lambda t: t[0], reverse=False)

		for data in self.resultArr:
			# text preprocess
			text = re.sub(r'@\w+', '', data[1])
			text = re.sub(
				'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '',
				text)
			text = re.sub(r'[\[]|[\]]', '', text)
			text = re.sub(r'[\r]|[\n]', ' ', text)
			text = re.sub(r'[.]|[ㆍ]', '', text)
			text = re.sub(r'#', ' ', text)

			# data[0] = datetime.datetime(int(data[0][0:4]), int(data[0][5:7]),
			# 									  int(data[0][8:10]),
			# 									  int(data[0][11:13]), int(data[0][14:16]),
			# 									  int(data[0][17:19]))

			sentPosArr = kkma.pos(text)
			inArr = []
			for outA in sentPosArr:
				# for inA in outA:
				inArr.append("/".join(outA))

			morph_arr = t.morphs(text)
			morphWords = [word for word in morph_arr if not word in tokens_ko]
			for word in morphWords:
				if not word in nounsArr:
					nounsArr.append(word)

			tokens_ko.extend(morphWords)

			newArr.append({"date":data[0],"sentence": "", "words": morph_arr, "score": 0})

			index = index + 1
			sentArr.append(";".join(inArr))

		index = 0
		for eaSent in sentArr:
			sentiScore = 0
			for corp in settings.KOSAC:
				if eaSent.find(corp['ngram']) > -1:
					if corp['max.value'] == 'NEG':
						sentiScore = sentiScore - float(corp['max.prop'])
					elif corp['max.value'] == 'POS':
						sentiScore = sentiScore + float(corp['max.prop'])

			newArr[index]["sentence"] = self.resultArr[index][1]
			newArr[index]["score"] = sentiScore

			index = index + 1

		self.resultArr2 = newArr

	def quit(self):
		"""
            Exit Method
        """
		self._driver.quit()

	def browse_target_page(self):
		# Browse Hashtags
		query = quote(self.query.encode("utf-8"))
		relative_url = query.strip('#')

		target_url = urljoin(settings.INSTA_DOMAIN, relative_url)

		self._driver.get(target_url)

	def scrape_tags_aco(self, number):
		"""
            scrape_tags method : scraping Instagram image URL & tags
        """

		last_post_num_pre = 0

		user_h1_tag = WebDriverWait(self._driver, 3).until(
			EC.presence_of_element_located((By.CSS_SELECTOR,
											"h1._rf3jb"))
		)

		user_id = user_h1_tag.get_attribute("title")

		while last_post_num_pre < number:

			WebDriverWait(self._driver, 3).until(
				EC.presence_of_element_located((By.XPATH,
												"//div[contains(@class, '_mck9w') and contains(@class,'_gvoze') and contains(@class,'_f2mse')]"))
			)

			user_post_list_new = self._driver.find_elements_by_xpath(
				"//div[contains(@class, '_mck9w') and contains(@class,'_gvoze') and contains(@class,'_f2mse')]")

			if len(user_post_list_new) < 1:
				self.quit()

			user_cur_post = user_post_list_new[last_post_num_pre].find_elements_by_xpath(".//a")[0]
			post_url = user_cur_post.get_attribute("href")

			post_url_arr = post_url.split('/')
			post_id = post_url_arr[len(post_url_arr) - 2]

			self._driver.get(post_url)

			single_post = WebDriverWait(self._driver, 3).until(
				EC.presence_of_element_located((By.XPATH, "//article[contains(@class, '_7hhq6')]"))
			)

			article_src = BeautifulSoup(single_post.get_attribute("innerHTML"), "html.parser")

			data_box = article_src.find('div', class_='_ebcx9')
			media_box = article_src.find('div', class_='_sxolz')

			write_date = data_box.find('time', class_='_p29ma').get('datetime')
			write_date_ymd = write_date.split('T')[0]

			ul = data_box.find('ul', class_='_b0tqa')
			li = ul.find_all('li')[0]

			cleanr = re.compile('<.*?>')
			text = re.sub(cleanr, '', str(li.span))

			media_src = media_box.find_all(['video', 'img'])[0].get('src')

			reg_date = datetime.datetime.now()

			instaSerial = InstaSerializer(data={"post_id": post_id
				, "user_id": user_id
				, "img": media_src
				, "text": text
				, "write_date": write_date
				, "reg_date": reg_date})

			if instaSerial.is_valid():
				row = instaSerial.validated_data

				# csvwriter.writerow([post_id, user_id, media_src, text, write_date, reg_date])
				try:
					instaSerial.save()
					self.resultArr.append((row['write_date'], row['text']))
				except IntegrityError:
					self.resultArr.append((row['write_date'], row['text']))
					pass

			last_post_num_pre = last_post_num_pre + 1
			# print("user's post count : {} ---------------------------------".format(last_post_num_pre))
			self._driver.back()

	def get(self, request, format=None):
		serializer = AnalyzerSerializer(data=request.query_params)

		if serializer.is_valid():
			formData = serializer.validated_data
			# 작업중 2017.11.15
			# ############################ 			CRAWL			###################################
			# session = request.session.load()

			# Setting
			# setting_path = '{}settings.json'.format(settings.CRAWL_PROJ_PATH)
			# authentication = '{}auth.json'.format(settings.CRAWL_PROJ_PATH)
            #
			# cmd_arr = [settings.GO_CRAWL_CMD, settings.GO_CRAWL_IN_PATH,
			# 		   '-n=' + str(5)]
            #
			# cmd_arr.append('-q={}'.format(formData['instaId']))
			# cmd_arr.append('-l')

			# # subprocess.call(cmd_arr)
			# # try:
			# temp = call(cmd_arr)
			# print(temp)

			temp = self.initializeC(formData['instaId'], 5)

			############################ 			ML			###################################
			# with open("new_data.json", "r") as jf:
			# 	dt = json.load(jf)

			text = formData['text']

			x_arr = []

			t = Twitter()
			vocab_fn = settings.VOCAB_FILENAME.format(settings.ML_VERSION)
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

			with graph.as_default():
				classes = model.predict(x_test, batch_size=settings.BATCH_SIZE)
				serializer.save()
				return Response({ "lstm":[serializer.data, classes],"aco":temp }, status=status.HTTP_201_CREATED)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CrawlView(APIView):
# 	parser_classes = (JSONParser,)
# 	authentication_classes = (SessionAuthentication, BasicAuthentication)
# 	permission_classes = (IsAuthenticated,)
#
# 	def get(self, request, format=None):
# 		# print(request.user)
#
# 		crawls = Crawl.objects.all()
# 		serializer = CrawlSerializer(crawls, many=True)
# 		return Response(serializer.data)

# class CrawlSaveView(APIView):
# 	parser_classes = (JSONParser,)
# 	authentication_classes = (SessionAuthentication, BasicAuthentication)
# 	permission_classes = (IsAuthenticated,)
#
# 	def get(self, request, format=None):
#
# 		serializer = CrawlSerializer(data=request.query_params)
#
# 		if serializer.is_valid():
#
# 			# 크롤링 실행
# 			data = serializer.validated_data
#
# 			now = datetime.datetime.now()
# 			# Setting
# 			setting = settings.CRAWL_SETTING
# 			csv_dir_prefix = '{}data'.format(settings.CRAWL_PROJ_PATH)
# 			setting_path = '{}settings.json'.format(settings.CRAWL_PROJ_PATH)
# 			authentication = '{}auth.json'.format(settings.CRAWL_PROJ_PATH)
#
# 			GO_CRAWL_PATH = settings.GO_CRAWL_FB_PATH if data.get('sns_kind') == 'fb' else settings.GO_CRAWL_IN_PATH
#
# 			DB_CURRENT_CNT = 0
#
# 			loop_cnt = int(data.get('number') / 500)
#
# 			# img directory check
# 			img_dir_path = os.path.join(settings.CRAWL_PROJ_PATH, 'img')
# 			if not os.path.exists(img_dir_path):
# 				os.makedirs(img_dir_path)
#
# 			# !! CHANGE FROM DB CONNECTION TO FILE SYSTEM !!
# 			DB_CNT = 0
# 			csv_filename = "{}-explore-{}".format(data.get('sns_kind'), now.strftime("%Y-%m-%d"))
# 			csv_file_loc = os.path.join(csv_dir_prefix, "{}.csv".format(csv_filename))
#
# 			if os.path.exists(csv_file_loc):
# 				DB_CNT = csv_len(csv_file_loc)
# 			else:
# 				with open(csv_file_loc, 'w') as file:
# 					file.writelines("id,img,text,has_tag,write_date,reg_date\n")
#
# 			DB_TOBE_CNT = DB_CNT + data.get('number')
#
# 			while DB_TOBE_CNT > DB_CURRENT_CNT:
#
# 				cmd_arr = [settings.GO_CRAWL_CMD, GO_CRAWL_PATH,
# 						   '-d=' + csv_file_loc,
# 						   '-t=' + data.get('crawl_type'),
# 						   '-n=' + str(500),
# 						   '-a=' + authentication,
# 						   '-s=' + setting_path,
# 						   '-e=' + data.get('env')]
#
# 				if data.get('query') != "":
# 					cmd_arr.append('-q={}'.format(data.get('query')))
# 				elif data.get('random'):
# 					cmd_arr.append('-r')
#
# 				cmd_arr.append('-l')
#
# 				print(cmd_arr)
# 				# subprocess.call(cmd_arr)
# 				# try:
# 				call(cmd_arr)
# 				# except TimeoutExpired as e:
# 				# 	continue
# 				# finally:
# 				# DB_CURRENT_CNT = collection.find({}).count()
# 				DB_CURRENT_CNT = csv_len(csv_file_loc)
#
# 			serializer.save()
# 			return Response(serializer.data, status=status.HTTP_201_CREATED)
# 		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CrawlMonitorView(APIView):
# 	parser_classes = (JSONParser,)
# 	authentication_classes = (SessionAuthentication, BasicAuthentication)
# 	permission_classes = (IsAuthenticated,)
#
# 	def get(self, request, format=None):
#
# 		data = request.query_params
#
# 		now = datetime.datetime.now()
# 		nowDate = now.strftime("%Y%m%d")
#
#
# 		filename = 'logs/log-' + data.get('env') + '.' + nowDate + '.log'
# 		filename = os.path.join(settings.DIR_PREFIX, filename)
#
# 		lines = []
# 		startNum = 0
#
# 		if not data.get('startNum'):
#
# 			with open(filename) as fp:
# 				for i, line in enumerate(fp):
# 					lines.append({'num':i,'text':line})
# 		else:
# 			startNum = int(data.get('startNum'))
#
# 			with open(filename) as fp:
# 				for i, line in enumerate(fp):
# 					if i > startNum:
# 						lines.append({'num': i, 'text': line})
#
# 		endNum = len(lines) + startNum
#
# 		return Response({'log':{
# 			'startNum':startNum,
# 			'endNum':endNum,
# 			'lines':lines
# 		}}, status=status.HTTP_200_OK)
#
# class CrawlCSVDataView(APIView):
# 	parser_classes = (JSONParser,)
# 	authentication_classes = (SessionAuthentication, BasicAuthentication)
# 	permission_classes = (IsAuthenticated,)
#
# 	def get(self, request, format=None):
#
# 		data = request.query_params
#
# 		now = datetime.datetime.now()
#
# 		csv_dir_prefix = '{}data'.format(settings.CRAWL_PROJ_PATH)
# 		csv_filename = "{}-explore-{}".format(data.get('sns_kind'), now.strftime("%Y-%m-%d"))
# 		csv_file_loc = os.path.join(csv_dir_prefix, "{}.csv".format(csv_filename))
#
#
# 		lines = []
# 		startNum = 0
#
# 		if not data.get('startNum'):
#
# 			with open(csv_file_loc) as fp:
# 				for i, line in enumerate(fp):
# 					lines.append({'num': i, 'text': line})
# 		else:
# 			startNum = int(data.get('startNum'))
#
# 			with open(csv_file_loc) as fp:
# 				for i, line in enumerate(fp):
# 					if i > startNum:
# 						lines.append({'num': i, 'text': line})
#
# 		endNum = len(lines) + startNum
#
# 		return Response({'csv': {
# 			'startNum': startNum,
# 			'endNum': endNum,
# 			'lines': lines
# 		}}, status=status.HTTP_200_OK)