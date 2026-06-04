#!/bin/bash

export PYSPARK_PYTHON='/bin/python3.6'

echo "Preprocessing"
spark-submit --conf spark.sql.autoBroadcastJoinThreshold=-1 --conf spark.driver.memory=2g preprocess.py

echo "Spark Analysis"
spark-submit analyze.py

echo "Hive Analysis"
hive -f hive.sql

echo "KMeans Clustering"
spark-submit kmeans.py

echo "Downloading results from HDFS"
rm -rf ../../data/results
hdfs dfs -get /user/maria_dev/kpop/results ../../data/results
