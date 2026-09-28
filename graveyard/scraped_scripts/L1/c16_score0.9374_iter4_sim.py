import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
df_grouped = df_union.groupby("CUSTOMERNAME", as_index=False)["ORDERNUMBER"].count()
df_grouped["ORDERNUMBER"] = df_grouped["ORDERNUMBER"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)