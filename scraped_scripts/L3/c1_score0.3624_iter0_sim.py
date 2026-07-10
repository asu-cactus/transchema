import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_grouped = df_all.groupby("Wrestler", as_index=False).sum()

years = [2013, 2014, 2015, 2016]
cols = ["Wins", "Losses", "Draws"]

result = pd.DataFrame()
result["Wrestler"] = df_grouped["Wrestler"]

for year in years:
    for col in cols:
        result[f"{year} {col}"] = 0

result = result[["Wrestler"] + [f"{year} {col}" for year in years for col in cols]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_1/target_multisource_mcts.csv", index=False)