from pathlib import Path
import pandas as pd
import shutil

DATA_DIR      = Path(__file__).parent / "data"
RAW_CSV       = DATA_DIR / "NaturalDisasters.csv"
CLEAN_CSV     = DATA_DIR / "DisastersCleaned.csv"

COLS = {
    "Year": "year",
    "Disaster Type": "type",
    "Country": "country",
    "Latitude": "lat",
    "Longitude": "lon",
    "Total Deaths": "deaths"
}

def extract() -> pd.DataFrame:
    if not RAW_CSV.exists():
        raise FileNotFoundError(
            f"{RAW_CSV} missing. Download it from Kaggle and place in data/."
        )
    temp = DATA_DIR / "working.csv"
    shutil.copy(RAW_CSV, temp)
    return pd.read_csv(temp)

def transform(df: pd.DataFrame) -> pd.DataFrame:
    tidy = (
        df[list(COLS.keys())]      
        .rename(columns=COLS)
        .dropna(subset=["lat", "lon", "year", "type"])        
        .reset_index(drop=True)
    )
    tidy["deaths"] = tidy["deaths"].fillna(0).astype(int)
    tidy["year"]   = tidy["year"].astype(int)
    tidy["search_key"] = (
        tidy["country"].str.lower() + " " + tidy["type"].str.lower()
    )
    return tidy

def load(df: pd.DataFrame) -> None: 
    df.to_csv(CLEAN_CSV, index=False)
    print("LOADED THE CSV")

def main(): 
    raw   = extract()
    clean = transform(raw)
    load(clean)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f" ETL failed - {e}")
        raise





