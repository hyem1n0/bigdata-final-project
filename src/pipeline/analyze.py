from pyspark.sql import SparkSession
from pyspark.sql import functions as F

HDFS_ROOT = "hdfs:///user/maria_dev/kpop"
IN_DATA = HDFS_ROOT + "/processed/kpop_joined"
OUT_DIR = HDFS_ROOT + "/results"

def main():
    spark = SparkSession.builder.appName("KpopAnalysis").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    df = spark.read.parquet(IN_DATA)
    df.createOrReplaceTempView("kpop")

    # Q1: 국가별 차트 잔류 기간 (Chart Sustainability)
    res1 = df.groupBy("track_id", "title", "region") \
        .agg(
            F.datediff(F.max("date"), F.min("date")).alias("chart_days"),
            F.count("*").alias("chart_entries")
        ) \
        .filter(F.col("chart_entries") > 1) \
        .groupBy("region") \
        .agg(
            F.avg("chart_days").alias("avg_chart_days"),
            F.avg("chart_entries").alias("avg_chart_entries"),
            F.count("track_id").alias("track_count")
        ).orderBy(F.col("avg_chart_days").desc())

    res1.show()
    res1.write.mode("overwrite").csv(OUT_DIR + "/q1", header=True)

    # Q2: 국가별 피처 평균
    res2 = spark.sql("""
        SELECT region,
               avg(danceability) as dance,
               avg(energy) as energy,
               avg(tempo) as tempo,
               count(*) as cnt
        FROM kpop
        GROUP BY region
        ORDER BY cnt DESC
    """)

    res2.show()
    res2.write.mode("overwrite").csv(OUT_DIR + "/q2", header=True)

    # Q3: 동일 곡의 국가별 스트리밍 수 vs 음향 특성 상관관계
    res3 = spark.sql("""
        SELECT region,
               corr(streams, danceability) as corr_dance,
               corr(streams, energy)       as corr_energy,
               corr(streams, tempo)        as corr_tempo,
               corr(streams, valence)      as corr_valence,
               count(*)                   as cnt
        FROM kpop
        GROUP BY region
        HAVING cnt > 100
        ORDER BY cnt DESC
    """)

    res3.show()
    res3.write.mode("overwrite").csv(OUT_DIR + "/q3", header=True)

    # Q4: 같은 곡의 국가별 스트리밍 쏠림 분석 (5개국 이상 차트인 곡 대상)
    res4 = spark.sql("""
        SELECT track_id, title,
               count(DISTINCT region)          AS country_count,
               avg(streams)                    AS avg_streams,
               stddev(streams)                 AS std_streams,
               stddev(streams) / avg(streams)  AS cv
        FROM kpop
        WHERE streams IS NOT NULL
        GROUP BY track_id, title
        HAVING count(DISTINCT region) >= 5
        ORDER BY cv DESC
    """)

    res4.show(20)
    res4.write.mode("overwrite").csv(OUT_DIR + "/q4", header=True)

    print("Analysis Done.")
    spark.stop()

if __name__ == "__main__":
    main()
