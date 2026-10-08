import pandas as pd
import re

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_31/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert GEO.id to string
df["GEO.id"] = df["GEO.id"].astype(str)

# Convert GEO.id2 to int, coercing errors to 0
df["GEO.id2"] = pd.to_numeric(df["GEO.id2"], errors='coerce').fillna(0).astype(int)

# Extract numeric part from GEO.display-label string and convert to int
# Example: "ZCTA5 91932" -> 91932
def extract_numeric_label(s):
    if pd.isna(s):
        return 0
    # Find last number in the string
    matches = re.findall(r'\d+', str(s))
    if matches:
        return int(matches[-1])
    else:
        return 0

df["GEO.display-label"] = df["GEO.display-label"].apply(extract_numeric_label).astype(int)

# Convert HD01_VD01 and HD02_VD01 to numeric, fill NaN with 0, convert to int
df["HD01_VD01"] = pd.to_numeric(df["HD01_VD01"], errors='coerce').fillna(0).astype(int)
df["HD02_VD01"] = pd.to_numeric(df["HD02_VD01"], errors='coerce').fillna(0).astype(int)

# Convert Year to int, fill NaN with 0
df["Year"] = pd.to_numeric(df["Year"], errors='coerce').fillna(0).astype(int)

# Group by key columns and sum the numeric columns
df_grouped = df.groupby(["GEO.id", "GEO.id2", "GEO.display-label", "Year"], as_index=False).agg({
    "HD01_VD01": "sum",
    "HD02_VD01": "sum"
})

# Reorder columns to match target schema
df_grouped = df_grouped[["GEO.id", "GEO.id2", "GEO.display-label", "HD01_VD01", "HD02_VD01", "Year"]]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv", index=False)