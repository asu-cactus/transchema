import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_79/training_1.csv", index_col=0)
df_target = df1[['city', 'fare']].copy()
df_target['fare'] = df_target['fare'].astype(float)
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length2_79/target_multisource_mcts.csv", index=False)