from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline

HDFS_ROOT = "hdfs:///user/maria_dev/kpop"
IN_DATA = HDFS_ROOT + "/processed/kpop_joined"
OUT_DIR = HDFS_ROOT + "/results/kmeans"

FEATURES = ["danceability", "energy", "tempo", "valence", "acousticness"]
K = 4 

if __name__ == "__main__":
    spark = SparkSession.builder.appName("KpopKMeans").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    df = spark.read.parquet(IN_DATA).dropna(subset=FEATURES).dropDuplicates(["track_id"])
    for f in FEATURES:
        df = df.withColumn(f, F.col(f).cast("double"))

    # 피처 벡터화 + 정규화
    assembler = VectorAssembler(inputCols=FEATURES, outputCol="features_raw")
    scaler = StandardScaler(inputCol="features_raw", outputCol="features")
    kmeans = KMeans(k=K, seed=42, featuresCol="features", predictionCol="cluster")

    pipeline = Pipeline(stages=[assembler, scaler, kmeans])
    model = pipeline.fit(df)

    result = model.transform(df)

    # 클러스터별 음향 특성 평균
    summary = result.groupBy("cluster").agg(
        F.avg("danceability").alias("avg_danceability"),
        F.avg("energy").alias("avg_energy"),
        F.avg("tempo").alias("avg_tempo"),
        F.avg("valence").alias("avg_valence"),
        F.count("track_id").alias("track_count")
    ).orderBy("cluster")

    summary.show()

    # 클러스터별 국가 분포 
    region_dist = result.groupBy("cluster", "region").agg(
        F.sum("streams").alias("total_streams")
    ).orderBy("cluster", F.col("total_streams").desc())

    region_dist.show(20)

    summary.write.mode("overwrite").csv(OUT_DIR + "/cluster_summary", header=True)
    region_dist.write.mode("overwrite").csv(OUT_DIR + "/cluster_region", header=True)

    print(f"KMeans Done. k={K}")
    spark.stop()
