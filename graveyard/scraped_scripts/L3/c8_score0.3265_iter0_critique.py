import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_8/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_8/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_8/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_8/training_3.csv"
]

agg_dfs = []
for i, path in enumerate(paths):
    year = 2013 + i
    df = pd.read_csv(path, index_col=0)
    # Aggregate by Wrestler summing Wins, Losses, Draws
    agg = df.groupby("Wrestler", as_index=False).agg({
        "Wins": "sum",
        "Losses": "sum",
        "Draws": "sum"
    })
    # Rename columns to match target schema
    agg = agg.rename(columns={
        "Wins": f"{year} Wins",
        "Losses": f"{year} Losses",
        "Draws": f"{year} Draws"
    })
    agg_dfs.append(agg)

# Join all aggregated yearly dataframes on Wrestler
from functools import reduce
df_merged = reduce(lambda left, right: pd.merge(left, right, on="Wrestler", how="outer"), agg_dfs)

# Convert numeric columns to Int64 dtype to allow NaNs
df_merged = df_merged.astype({
    col: 'Int64' for col in df_merged.columns if col != "Wrestler"
})

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_8/target_multisource_mcts.csv", index=False)