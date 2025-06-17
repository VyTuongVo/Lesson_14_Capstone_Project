import sqlite3
import pandas as pd

CSV_FILE    = "american_league_team_standings_2000_2025_sample.csv"
DB_FILE     = "mlb_history.db"
TABLE_NAME  = "team_standings"

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    # Wins and lost → int
    for col in ("Wins", "Losses"):
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    # WP into float --> it have decimal numbervs 
    if "WP" in df:
        df["WP"] = pd.to_numeric(
            df["WP"].astype(str).str.replace(r"[^\d\.]", "", regex=True),
            errors="coerce"
        )
    # GB into float 
    if "GB" in df:
        df["GB"] = pd.to_numeric(
            df["GB"].astype(str)
                   .str.replace("½", ".5")
                   .str.replace(r"[^\d\.]", "", regex=True),
            errors="coerce"
        )
    return df

def infer_type(series: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(series):
        return "INTEGER"
    if pd.api.types.is_float_dtype(series):
        return "REAL"
    return "TEXT"

def main():
    df = pd.read_csv(CSV_FILE)

    # Dude to inconsistency, I will be dropping Pauyroll
    df = df.drop(columns=["Payroll"], errors="ignore")

    df = clean_df(df)

    # 
    cols  = df.columns.tolist()
    types = [infer_type(df[c]) for c in cols]
    schema = ", ".join(f'"{c}" {t}' for c, t in zip(cols, types))

    conn = sqlite3.connect(DB_FILE)
    cur  = conn.cursor()
    try:
        cur.execute(f'DROP TABLE IF EXISTS "{TABLE_NAME}"')
        cur.execute(f'CREATE TABLE "{TABLE_NAME}" ({schema})')

        placeholders = ", ".join("?" for _ in cols)
        insert_sql   = f'INSERT INTO "{TABLE_NAME}" ({", ".join(cols)}) VALUES ({placeholders})'
        cur.executemany(insert_sql, df[cols].values.tolist())
        conn.commit()
        print(f"Imported {len(df)} rows into '{TABLE_NAME}' in '{DB_FILE}'")
    except Exception as e:
        conn.rollback()
        print(f" XXX  Error during import: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
