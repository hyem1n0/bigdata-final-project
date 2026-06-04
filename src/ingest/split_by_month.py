import os
import sys
import pandas as pd

DATA_DIR = "../../data/raw"
CSV_PATH = os.path.join(DATA_DIR, "charts/charts.csv")
SAVE_DIR = os.path.join(DATA_DIR, "charts_monthly")

def split_data():
    if not os.path.exists(CSV_PATH):
        print("Error: charts.csv not found.")
        return

    os.makedirs(SAVE_DIR, exist_ok=True)
    
    chunk_size = 500000

    written = set()

    for chunk in pd.read_csv(CSV_PATH, chunksize=chunk_size, low_memory=False):
        chunk['date'] = pd.to_datetime(chunk['date'], errors='coerce')
        chunk = chunk.dropna(subset=['date'])
        chunk['ym'] = chunk['date'].dt.strftime('%Y-%m')

        for ym, group in chunk.groupby('ym'):
            out_name = os.path.join(SAVE_DIR, f"{ym}.csv")
            group = group.drop(columns=['ym'])
            if ym in written:
                group.to_csv(out_name, mode='a', header=False, index=False)
            else:
                group.to_csv(out_name, index=False)
                written.add(ym)
                print(f"Saved {ym}.csv")

if __name__ == "__main__":
    split_data()
    print("Finished.")
