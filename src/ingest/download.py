import os
import sys
import subprocess

# 데이터 저장 경로
RAW_DATA_PATH = "../../data/raw"

def get_data():
    if not os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json")):
        print("Error: kaggle.json not found.")
        sys.exit(1)

    datasets = {
        "charts": "dhruvildave/spotify-charts",
        "features": "rodolfofigueroa/spotify-12m-songs",
    }

    force = "--force" in sys.argv

    if not os.path.exists(RAW_DATA_PATH):
        os.makedirs(RAW_DATA_PATH)

    for key, slug in datasets.items():
        target = os.path.join(RAW_DATA_PATH, key)
        
        if os.path.exists(target) and not force:
            if any(f.endswith(".csv") for f in os.listdir(target)):
                print(f"Skip: {key} already exists")
                continue

        os.makedirs(target, exist_ok=True)
        print(f"Downloading {key}...")
        
        res = subprocess.run([
            "kaggle", "datasets", "download", "-d", slug, "-p", target, "--unzip"
        ])
        
        if res.returncode != 0:
            print(f"Failed to download {key}")
            sys.exit(1)

if __name__ == "__main__":
    get_data()
    print("Done.")
