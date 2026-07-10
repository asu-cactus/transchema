import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by WarNum and aggregate WhereFought by min
df_grouped = df.groupby('WarNum', as_index=False).agg({'WhereFought': 'min'})

# Reorder columns to match target schema: ['WhereFought', 'WarNum']
df_final = df_grouped[['WhereFought', 'WarNum']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)