# 2021 South Korea Chart Songs: Global Streaming Analysis
Spark 및 Hive를 활용한 한국 차트 곡의 글로벌 소비 패턴 분석

---

## 1. 문제 정의 (Problem Definition)

### 배경 및 목적

최근 K-POP은 전 세계 음악 시장에서 큰 영향력을 가지며 글로벌 팬층을 확대하고 있다. 그러나 같은 한국 차트 곡이라도 국가별 문화와 음악 소비 성향에 따라 소비 방식이 다를 수 있다.
2021년 한국 Spotify 차트에 오른 곡들이 전 세계 70개국에서 어떻게 소비되는지를 파악하기 위해, 차트 잔류 기간·음향 특성·스트리밍 집중도 등을 국가별로 비교 분석하여 글로벌 K-Pop 소비 패턴에 대한 인사이트를 도출하고자 한다.

### 분석 질문

- Q1. 국가별로 한국 차트 곡의 평균 차트 잔류 기간(avg chart days)이 어떻게 다른가?
- Q2. 국가별 평균 음향 특성(danceability, energy, tempo)에 유의미한 차이가 있는가?
- Q3. 국가별로 스트리밍 수와 음향 특성(danceability, energy, tempo, valence) 간의 상관관계는 어떠한가?
- Q4. 5개국 이상에서 차트인한 곡 중, 국가별 스트리밍 수의 편차가 큰 곡은 무엇인가?

### 수집 및 사용할 데이터

- **Spotify Charts Dataset** (Kaggle): 2017년~2021년 국가별 일별 Top 200 차트 데이터 (약 2,600만 행, 3.2GB)
- **Spotify 1.2M+ Songs Audio Features** (Kaggle): 120만 곡 이상의 템포, 댄스 적합도 등 음향 특성 데이터 (330MB)

샘플 데이터: `data/raw/sample/`

---

## 2. 기술 스택 (Tech Stack)

- **데이터 수집**: Python (Kaggle API), Shell Script
- **데이터 저장**: HDFS
- **데이터 전처리**: Apache Spark (PySpark)
- **데이터 분석**: Apache Hive (HiveQL), Spark SQL
- **머신러닝**: Spark MLlib (KMeans)
- **시각화**: Python Matplotlib, Seaborn
- **자동화**: Makefile

---

## 3. 구현 계획 (Implementation Plan)

### 데이터 수집 (Data Ingestion)
- Kaggle API를 통해 spotify-charts 및 spotify-12m-songs 데이터셋 다운로드
- 전체 데이터를 월별로 분할하여 HDFS에 적재

### 데이터 저장 및 전처리 (Storage & Preprocessing)
- 수집된 데이터를 HDFS에 적재
- Apache Spark로 2021년 한국 차트인 곡 필터링 및 음향 피처 JOIN
- 결측치 처리 및 Parquet 포맷으로 저장

### 데이터 분석 및 머신러닝 (Analysis & Machine Learning)
- **통계 분석 (Hive / Spark SQL)**: 국가별 차트 잔류 기간, 음향 특성 평균, 스트리밍 상관관계, 스트리밍 쏠림(CV) 분석
- **군집 분석 (Spark MLlib)**: K-Means(k=4)로 한국 차트 곡들을 음악적 스타일 군집으로 분류하고 국가별 소비 패턴 파악

### 결과 시각화 (Visualization)
- 분석된 군집 및 통계 결과를 Matplotlib/Seaborn 차트로 구현

---

## 4. 실행 방법 (HDP Sandbox 기준)

### 환경

- HDP Sandbox (HDP 2.6.5), Python 3.6, Spark 2.x, Hive 1.2.x
- HDFS 경로: `/user/maria_dev/kpop`

### 사전 준비

```bash
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Step 1. 데이터 수집 및 HDFS 업로드

```bash
make download   # Kaggle에서 데이터 다운로드
make split      # 월별 CSV 분할
make upload     # HDFS 업로드
```

### Step 2. 전처리 / 분석 / 클러스터링 (HDP Sandbox 내 실행)

```bash
cd src/pipeline
bash run.sh
```

실행 순서: `preprocess.py` → `analyze.py` → `hive.sql` → `kmeans.py` → HDFS 결과 로컬 저장

### Step 3. 시각화

```bash
make visualize
```

결과 그래프는 `results/figures/`에 저장

---

## 5. 결과 요약

- **국가별 차트 잔류 기간 (Q1)**: South Africa(191일), Australia(189일), UAE(188일) 순으로 한국 차트 곡을 오래 소비. 영미권 및 동남아시아 국가에서 지속성이 높게 나타남
- **국가별 음향 특성 (Q2)**: 한국은 energy가 정규화 기준 1.00으로 전체 국가 중 가장 높음. Hungary는 danceability(1.00), Slovakia는 tempo(1.00)가 최고치로, 국가마다 선호 음향 특성이 뚜렷하게 다름
- **스트리밍 상관관계 (Q3)**: 한국에서 Valence(긍정성)와 스트리밍 수 상관관계가 0.30으로 가장 높음. 대부분의 국가에서 Tempo는 스트리밍과 음의 상관관계를 보임
- **스트리밍 쏠림 분석 (Q4)**: CV가 높은 곡(특정 국가 집중)은 Levitating, Mood 등 서양 팝이 주를 이루고, CV가 낮은 곡(고르게 소비)은 FAKE LOVE, Euphoria, Blue & Grey 등 K-Pop이 다수를 차지함
- **KMeans 클러스터링**: 한국 차트 곡을 4개 스타일로 분류. Cluster 2(Pop/Mid)는 tempo가 가장 높고, Cluster 0(Dance/Upbeat)은 energy가 두드러지며, Cluster 3(R&B/Groove)은 전반적으로 낮고 안정적인 음향 특성을 보임

---

## 기대 효과

- 국가별 K-POP 선호 특성 분석
- 글로벌 음악 시장 트렌드 파악
- 데이터 기반 마케팅 전략 도출

---

## AI Tool Usage

- Claude: 코드 디버깅 (src/pipeline/preprocess.py, src/pipeline/analyze.py, src/pipeline/hive.sql, src/pipeline/kmeans.py, src/analyze/visualize.py), 슬라이드 구성 아이디어 검토, Makefile 구조 제안

---

## 참고 자료

- [Spotify Charts Dataset (Kaggle)](https://www.kaggle.com/datasets/dhruvildave/spotify-charts)
- [Spotify 1.2M+ Songs Audio Features (Kaggle)](https://www.kaggle.com/datasets/rodolfofigueroa/spotify-12m-songs)
- [Apache Spark Docs](https://spark.apache.org/docs/latest/)
- [Apache Hive Docs](https://hive.apache.org/)
- [Spark MLlib Guide](https://spark.apache.org/docs/latest/ml-guide.html)
