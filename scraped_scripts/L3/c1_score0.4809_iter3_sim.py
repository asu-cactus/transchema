import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_1/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_1/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_1/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_1/training_3.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_grouped = df_all.groupby("Wrestler", as_index=False).sum()

years = [2013, 2014, 2015, 2016]
metrics = ["Wins", "Losses", "Draws"]

result = df_grouped.copy()
for year in years[1:]:
    for metric in metrics:
        result[f"{year} {metric}"] = 0

result = result.rename(columns={
    "Wins": "2013 Wins",
    "Losses": "2013 Losses",
    "Draws": "2013 Draws",
})

cols_order = ["Wrestler"]
for year in years:
    for metric in metrics:
        cols_order.append(f"{year} {metric}")

result = result[cols_order]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_1/target_multisource_mcts.csv", index=False)