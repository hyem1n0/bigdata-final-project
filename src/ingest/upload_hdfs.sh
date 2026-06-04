#!/bin/bash

HDFS_BASE="/user/maria_dev/kpop"
LOCAL_RAW="../../data/raw"

hdfs dfs -mkdir -p ${HDFS_BASE}/raw/charts_monthly
hdfs dfs -mkdir -p ${HDFS_BASE}/raw/features
hdfs dfs -mkdir -p ${HDFS_BASE}/raw/meta
hdfs dfs -mkdir -p ${HDFS_BASE}/processed
hdfs dfs -mkdir -p ${HDFS_BASE}/results

# 월별 차트 업로드
for f in ${LOCAL_RAW}/charts_monthly/*.csv; do
    hdfs dfs -put -f "$f" ${HDFS_BASE}/raw/charts_monthly/
done

# 피처 업로드
if [ -f ${LOCAL_RAW}/features/tracks_features.csv ]; then
    hdfs dfs -put -f ${LOCAL_RAW}/features/tracks_features.csv ${HDFS_BASE}/raw/features/
fi

# 메타 정보 업로드
if [ -f ${LOCAL_RAW}/kpop_urls.txt ]; then
    hdfs dfs -put -f ${LOCAL_RAW}/kpop_urls.txt ${HDFS_BASE}/raw/meta/
fi

hdfs dfs -ls -R ${HDFS_BASE}
