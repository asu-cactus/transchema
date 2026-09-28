import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby("hero").agg(
    matches=pd.NamedAgg(column="matches", aggfunc="sum"),
    winrate_min=pd.NamedAgg(column="winrate", aggfunc="min"),
    winrate_max=pd.NamedAgg(column="winrate", aggfunc="max"),
).reset_index()

agg["winrate"] = (agg["winrate_min"] + agg["winrate_max"]) / 2
agg = agg.drop(columns=["winrate_min", "winrate_max"])

disadvantage = df_all.groupby("hero")["disadvantage"].mean().reset_index()

result = pd.merge(agg, disadvantage, on="hero", how="left")

result = result[["hero", "disadvantage", "winrate", "matches"]]

result["hero"] = result["hero"].astype(str)
result["disadvantage"] = result["disadvantage"].astype(float)
result["winrate"] = result["winrate"].astype(float)
result["matches"] = result["matches"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)