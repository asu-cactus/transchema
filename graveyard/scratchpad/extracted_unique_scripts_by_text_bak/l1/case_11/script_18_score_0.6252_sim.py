import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
df_target = df_union[['sex', 'births']].copy()
df_target['sex'] = df_target['sex'].astype(str)
df_target['births'] = pd.to_numeric(df_target['births'], errors='coerce').fillna(0).astype(int)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)