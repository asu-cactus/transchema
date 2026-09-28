import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

df['matches'] = pd.to_numeric(df['matches'], errors='coerce').fillna(0).astype(int)
df['disadvantage'] = pd.to_numeric(df['disadvantage'], errors='coerce')
df['winrate'] = pd.to_numeric(df['winrate'], errors='coerce')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)