# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

HDFS_PATH = "hdfs:///user/maria_dev/kpop"
CHARTS_DIR = HDFS_PATH + "/raw/charts_monthly"
FEATURES_FILE = HDFS_PATH + "/raw/features/tracks_features.csv"
SAVE_PATH = HDFS_PATH + "/processed/kpop_joined"

NUM_COLS = ["danceability", "energy", "tempo", "valence", "acousticness",
            "loudness", "speechiness", "instrumentalness", "liveness"]

def run_preprocess():
    spark = SparkSession.builder.appName("KpopJob").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    df_charts = spark.read.csv(CHARTS_DIR, header=True, inferSchema=False)

    df_charts = df_charts.filter(F.substring(F.col("date"), 1, 4) == "2021")
    df_charts = df_charts.withColumn(
        "track_id", F.regexp_extract(F.col("url"), r"/track/([A-Za-z0-9]+)", 1)
    )
    df_charts = df_charts.withColumn("date", F.to_date(F.col("date"), "yyyy-MM-dd"))
    df_charts = df_charts.withColumn("streams", F.col("streams").cast("long"))

    kpop_list = df_charts.filter(
        F.lower(F.trim(F.col("region"))).contains("korea")
    ).select("track_id").distinct()

    print("KR tracks: " + str(kpop_list.count()))

    df_kpop = df_charts.join(kpop_list, "track_id")

    df_feat = spark.read.csv(FEATURES_FILE, header=True, inferSchema=False)
    for col_name in NUM_COLS:
        df_feat = df_feat.withColumn(col_name, F.col(col_name).cast("double"))
    df_feat = df_feat.dropna(subset=["id"] + NUM_COLS)

    final_df = df_kpop.join(df_feat, df_kpop.track_id == df_feat.id).drop(df_feat.id)

    print("Finished. Count: " + str(final_df.count()))
    final_df.write.mode("overwrite").parquet(SAVE_PATH)
    spark.stop()

if __name__ == "__main__":
    run_preprocess()
