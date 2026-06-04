import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import glob
import os

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(BASE, "results", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

def load_csv(rel_path):
    path = os.path.join(BASE, rel_path)
    files = glob.glob(path + "/*.csv")
    return pd.concat([pd.read_csv(f, header=0) for f in files], ignore_index=True)


# Q1: 국가별 차트 잔류 기간 (Chart Sustainability)
def plot_q1():
    df = load_csv("data/results/q1")
    df.columns = ["region", "avg_chart_days", "avg_chart_entries", "track_count"]
    df = df.dropna()
    df["avg_chart_days"] = pd.to_numeric(df["avg_chart_days"], errors="coerce")
    df = df.dropna(subset=["avg_chart_days"]).sort_values("avg_chart_days", ascending=False).head(20)

    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="avg_chart_days", y="region", palette="Blues_d")
    plt.title("Avg Chart Sustainability by Region (2021)")
    plt.xlabel("Average Days on Chart")
    plt.ylabel("Region")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/q1_chart_sustainability.png", dpi=150)
    plt.close()
    print("Saved q1")


# Q2: 국가별 음향 특성 히트맵
def plot_q2():
    df = load_csv("data/results/q2")
    df.columns = ["region", "danceability", "energy", "tempo", "cnt"]
    df = df.dropna().sort_values("cnt", ascending=False).head(20)

    heatmap_data = df.set_index("region")[["danceability", "energy", "tempo"]]
    heatmap_data = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())

    plt.figure(figsize=(8, 10))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="YlOrRd")
    plt.title("Audio Features by Region (Normalized)")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/q2_region_heatmap.png", dpi=150)
    plt.close()
    print("Saved q2")


# Q3: 국가별 스트리밍 수 vs 음향 특성 상관관계
def plot_q3():
    df = load_csv("data/results/q3")
    df.columns = ["region", "corr_dance", "corr_energy", "corr_tempo", "corr_valence", "cnt"]
    df = df.dropna()
    for col in ["corr_dance", "corr_energy", "corr_tempo", "corr_valence"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna().sort_values("cnt", ascending=False).head(20)

    heatmap_data = df.set_index("region")[["corr_dance", "corr_energy", "corr_tempo", "corr_valence"]]
    heatmap_data.columns = ["Danceability", "Energy", "Tempo", "Valence"]

    plt.figure(figsize=(8, 10))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", center=0)
    plt.title("Correlation: Streams vs Audio Features by Region (2021)")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/q3_corr_heatmap.png", dpi=150)
    plt.close()
    print("Saved q3")


# Q4: 국가별 스트리밍 쏠림 분석 — CV 기준 상위/하위 15곡 비교
def plot_q4():
    df = load_csv("data/results/q4")
    df.columns = ["track_id", "title", "country_count", "avg_streams", "std_streams", "cv"]
    df = df.dropna()
    df["cv"] = pd.to_numeric(df["cv"], errors="coerce")
    df["avg_streams"] = pd.to_numeric(df["avg_streams"], errors="coerce")
    df = df.dropna(subset=["cv", "title"]).sort_values("cv", ascending=False)

    top15 = df.head(15)
    bot15 = df.tail(15).sort_values("cv", ascending=True)
    combined = pd.concat([top15, bot15])
    combined["label"] = combined["title"].str[:30]
    combined["type"] = ["쏠림" ] * 15 + ["균등"] * 15

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, group, color, title in zip(
        axes,
        [top15, bot15],
        ["salmon", "steelblue"],
        ["Top 15 Concentrated (High CV)", "Top 15 Evenly Spread (Low CV)"]
    ):
        labels = group["title"].fillna("Unknown").astype(str).str[:25]
        ax.barh(labels, group["cv"], color=color)
        ax.set_xlabel("CV (Coefficient of Variation)")
        ax.set_title(title)
        ax.invert_yaxis()

    plt.suptitle("South Korea Chart Songs: Streaming Concentration by Country")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/q4_streaming_concentration.png", dpi=150)
    plt.close()
    print("Saved q4")


# K-Means: 클러스터별 음향 특성 레이더 차트
def plot_kmeans():
    df = load_csv("data/results/kmeans/cluster_summary")
    df.columns = ["cluster", "danceability", "energy", "tempo", "valence", "track_count"]
    df = df.dropna()
    df["tempo"] = df["tempo"] / df["tempo"].max() 

    features = ["danceability", "energy", "tempo", "valence"]
    angles = [i / len(features) * 2 * 3.14159 for i in range(len(features))]
    angles += angles[:1]

    fig, axes = plt.subplots(1, len(df), figsize=(14, 4), subplot_kw=dict(polar=True))
    cluster_names = ["Dance/Upbeat", "Ballad/Calm", "Pop/Mid", "R&B/Groove"]

    for i, (_, row) in enumerate(df.iterrows()):
        vals = row[features].tolist()
        vals += vals[:1]
        ax = axes[i]
        ax.plot(angles, vals, linewidth=2)
        ax.fill(angles, vals, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(features, size=8)
        ax.set_title(f"Cluster {int(row['cluster'])}\n{cluster_names[i]}", size=9)

    plt.suptitle("South Korea Chart Songs: Music Style Clusters (K-Means, k=4)")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/kmeans_radar.png", dpi=150)
    plt.close()
    print("Saved kmeans")


if __name__ == "__main__":
    plot_q1()
    plot_q2()
    plot_q3()
    plot_q4()
    plot_kmeans()
    print(f"All figures saved to {OUT_DIR}")
