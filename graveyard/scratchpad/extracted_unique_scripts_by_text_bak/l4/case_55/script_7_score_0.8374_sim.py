import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

agg_df = df_all.groupby("WarNum").agg(WhereFought_min=("WhereFought", "min"), WhereFought_max=("WhereFought", "max")).reset_index()

agg_df["WhereFought"] = agg_df[["WhereFought_min", "WhereFought_max"]].min(axis=1)

result = agg_df[["WarNum", "WhereFought"]].astype({"WarNum": int, "WhereFought": int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)