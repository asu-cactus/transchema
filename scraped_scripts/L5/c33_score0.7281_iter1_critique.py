import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_33/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert columns to appropriate types
df["GEO.id2"] = df["GEO.id2"].astype(str)
df["GEO.id"] = pd.to_numeric(df["GEO.id2"], errors='coerce').astype("Int64")
# Do NOT convert GEO.display-label to numeric, instead set it later to constant 5
df["HD01_VD01"] = pd.to_numeric(df["HD01_VD01"], errors='coerce').fillna(0).astype("Int64")
df["HD02_VD01"] = pd.to_numeric(df["HD02_VD01"], errors='coerce').fillna(0).astype("Int64")
df["Year"] = pd.to_numeric(df["Year"], errors='coerce').fillna(0).astype("Int64")

# Group by GEO.id2 and GEO.id, aggregate sums and max year
agg_df = df.groupby(["GEO.id2", "GEO.id"], as_index=False).agg({
    "HD01_VD01": "sum",
    "HD02_VD01": "sum",
    "Year": "max"
})

# Add GEO.display-label as constant 5 (integer)
agg_df["GEO.display-label"] = 5

# Reorder columns to match target schema
agg_df = agg_df[["GEO.id2", "GEO.id", "GEO.display-label", "HD01_VD01", "HD02_VD01", "Year"]]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_33/target_multisource_mcts.csv", index=False)