import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_8/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_8/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_8/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_8/training_3.csv"
]

dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    year = 2013 + i
    df = df.rename(columns={
        "Wins": f"{year} Wins",
        "Losses": f"{year} Losses",
        "Draws": f"{year} Draws"
    })
    dfs.append(df)

from functools import reduce
df_merged = reduce(lambda left, right: pd.merge(left, right, on="Wrestler", how="outer"), dfs)

df_merged = df_merged.astype({
    col: 'Int64' for col in df_merged.columns if col != "Wrestler"
})

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_8/target_multisource_mcts.csv", index=False)