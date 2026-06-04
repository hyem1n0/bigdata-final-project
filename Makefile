# 프로젝트 실행용 Makefile

all: download split upload run visualize

download:
	cd src/ingest && python3 download.py

split:
	cd src/ingest && python3 split_by_month.py

upload:
	cd src/ingest && bash upload_hdfs.sh

run:
	cd src/pipeline && bash run.sh

visualize:
	python3 src/analyze/visualize.py

clean:
	rm -rf data/raw/*
