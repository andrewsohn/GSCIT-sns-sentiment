> 고려대학교 컴퓨터정보통신대학원 :: 2017 빅데이터 응용 세미나1
> 
> 인스타그램 이미지&해쉬태그 데이터 기반 감성분석

인스타그램 한국어 감성 분석기
===


Requires
------------------
 * `python 3`
 * `virtualenv`
 * `keras`
 * `tensorflow `
 * `konlpy `
 * `nltk`
 * `numpy`
 * `sklearn`
 * `h5py `


Notice
------------------
Mac환경에서는 GIT을 통하여 `jpype` 라이브러리를 수동 설치 하여야 한다.
> jpype github : https://github.com/originell/jpype.git

	$ cd {YOUR APP NAME}/gitsrc
	$ git clone https://github.com/originell/jpype.git
	$ cd jpype
	$ python setup.py install

반드시 `./data/`하위에 CSV파일(HEADER형태: text, class)을 넣어두어야 작동한다.

API Documentation
------------------
학습 모델을 생성하기 위해서는 반드시 아래의 커맨드 순서를 지켜야 하며 `setWordMap.py`와 `word2vec.py`는 `-d` 값을 넣어서 실행해야 한다.

**setWordMap.py** :
> 입력 데이터의 모든 텍스트를 단어 단위로 나누어 JSON형태의 Word Map을 생성 

	$ python setWordMap.py -t o -d ./data/lstm_data171101.csv
	
	> 결과: ./data/ 디렉토리에 위치하는 json 파일

**word2vec.py** :
> 개별 입력 데이터를 vector array로 변환한 뒤 최종 전처리 데이터 npz 파일 생성

	$ python word2vec.py -t o -d ./data/lstm_data171101.csv

	> 결과: ./in/ 디렉토리에 위치하는 npz 파일

**lstm.py** :	
> LSTM 모델 생성 후 학습 실시 종료 후 모델 h5 파일 생성

	$ python lstm.py -t o

	> 결과: ./out/ 디렉토리에 위치하는 h5 파일

**getDataSet.py** :		
> 참조 파일이며 입력 데이터를 가공하는 함수를 포함

	$ python getDataSet.py

### Arguments
- `-t`, `--type` : 런 타입, 모델링 타입을 아래의 파라미터값과 함께 입력
	- `n` : newly create	신규 생성
	- `o` : overwrite on current version 덮어쓰기

- `-d`, `--data_file` : 데이터 파일, CSV 파일 형식의 인스타그램 데이터 경로 입력
	- eg) ./data/lstm_data171101.csv
	- CSV파일 헤더 :  'text', 'class'
- `-v`, `--version` : 버전, 현재 버전을 출력(versions.json내 관리)

Get Started
------------------

### 1. Python 가상화 
	$ virtualenv -p python3 {YOUR APP NAME}
	
### 2. 가상환경 Activation
	$ source {YOUR APP NAME}/bin/activate

### 3. 패키지 인스톨
	$ cd {YOUR APP NAME}
	$ pip install -r requirements.txt

Change Log
------------------
 * `v 1.0.0`
	 * [start] app initiated
	 * [update] facebook crawling added


