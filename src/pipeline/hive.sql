CREATE DATABASE IF NOT EXISTS kpop;
USE kpop;

-- 차트 테이블 (OpenCSVSerde 사용)
CREATE EXTERNAL TABLE IF NOT EXISTS charts (
    title       STRING,
    chart_rank  STRING,
    chart_date  STRING,
    artist      STRING,
    url         STRING,
    region      STRING,
    chart       STRING,
    trend       STRING,
    streams     STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\""
)
LOCATION 'hdfs:///user/maria_dev/kpop/raw/charts_monthly'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 피처 테이블 (OpenCSVSerde 사용)
CREATE EXTERNAL TABLE IF NOT EXISTS features (
    id               STRING,
    name             STRING,
    album            STRING,
    album_id         STRING,
    artists          STRING,
    artist_ids       STRING,
    track_number     STRING,
    disc_number      STRING,
    explicit         STRING,
    danceability     STRING,
    energy           STRING,
    song_key         STRING,
    loudness         STRING,
    mode             STRING,
    speechiness      STRING,
    acousticness     STRING,
    instrumentalness STRING,
    liveness         STRING,
    valence          STRING,
    tempo            STRING,
    duration_ms      STRING,
    time_signature   STRING,
    song_year        STRING,
    release_date     STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\""
)
LOCATION 'hdfs:///user/maria_dev/kpop/raw/features'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 분석용 뷰 (2021년 데이터만, 타입 캐스팅 포함)
CREATE OR REPLACE VIEW kpop_view AS
SELECT
    c.title, 
    CAST(c.chart_rank AS INT) AS chart_rank, 
    c.chart_date, 
    c.artist, 
    c.url,
    c.region, 
    c.chart, 
    c.trend, 
    CAST(c.streams AS BIGINT) AS streams,
    regexp_extract(c.url, '/track/([A-Za-z0-9]+)', 1) AS track_id,
    CAST(f.danceability AS DOUBLE) AS danceability, 
    CAST(f.energy AS DOUBLE) AS energy, 
    CAST(f.tempo AS DOUBLE) AS tempo, 
    CAST(f.valence AS DOUBLE) AS valence
FROM charts c
JOIN features f ON regexp_extract(c.url, '/track/([A-Za-z0-9]+)', 1) = f.id
WHERE c.url IN (
    SELECT url FROM charts
    WHERE LOWER(TRIM(region)) LIKE '%korea%' AND chart_date LIKE '2021%'
)
AND c.chart_date LIKE '2021%';

-- Q1: 국가별 차트 잔류 기간 (Chart Sustainability)
INSERT OVERWRITE DIRECTORY 'hdfs:///user/maria_dev/kpop/results/hive_q1'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT
    region,
    avg(chart_days)    AS avg_chart_days,
    avg(chart_entries) AS avg_chart_entries,
    count(*)           AS track_count
FROM (
    SELECT track_id, region,
           datediff(max(chart_date), min(chart_date)) AS chart_days,
           count(*)                                   AS chart_entries
    FROM kpop_view
    GROUP BY track_id, region
    HAVING count(*) > 1
) t
GROUP BY region
ORDER BY avg_chart_days DESC;

-- Q2: 국가별 음향 특성 평균
INSERT OVERWRITE DIRECTORY 'hdfs:///user/maria_dev/kpop/results/hive_q2'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT region,
       avg(danceability) AS danceability,
       avg(energy)       AS energy,
       avg(tempo)        AS tempo,
       count(*)          AS cnt
FROM kpop_view
GROUP BY region
ORDER BY cnt DESC;

-- Q3: 국가별 스트리밍 수와 음향 특성 상관관계
INSERT OVERWRITE DIRECTORY 'hdfs:///user/maria_dev/kpop/results/hive_q3'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT region,
       corr(streams, danceability) AS corr_dance,
       corr(streams, energy)       AS corr_energy,
       corr(streams, tempo)        AS corr_tempo,
       corr(streams, valence)      AS corr_valence,
       count(*)                    AS cnt
FROM kpop_view
WHERE streams IS NOT NULL
GROUP BY region
HAVING count(*) > 100
ORDER BY cnt DESC;

-- Q4: 같은 곡의 국가별 스트리밍 쏠림 분석 (5개국 이상 차트인 곡 대상)
INSERT OVERWRITE DIRECTORY 'hdfs:///user/maria_dev/kpop/results/hive_q4'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT
    track_id,
    title,
    count(DISTINCT region)               AS country_count,
    avg(streams)                         AS avg_streams,
    stddev_pop(streams)                  AS std_streams,
    stddev_pop(streams) / avg(streams)   AS cv
FROM kpop_view
WHERE streams IS NOT NULL
GROUP BY track_id, title
HAVING count(DISTINCT region) >= 5
ORDER BY cv DESC
LIMIT 30;
