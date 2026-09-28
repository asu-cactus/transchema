import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_40/training_0.csv", index_col=0)

df_target = df0[['school_name', 'reading_score']].copy()
df_target['reading_score'] = df_target['reading_score'].astype(float)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length2_40/target_multisource_mcts.csv", index=False)