import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_3.csv", index_col=0)

# Join Source1 and Source2 on County (inner join)
df12 = pd.merge(df1, df2, on="County", how="inner")

# Join the above with Source0 on County (inner join)
df012 = pd.merge(df12, df0, on="County", how="inner")

# Join the above with Source3 on County (left join to keep all counties from df012)
df_all = pd.merge(df012, df3, on="County", how="left")

# Select only columns needed in target schema
df_all = df_all[['County', 'm1401', 'm1403']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)