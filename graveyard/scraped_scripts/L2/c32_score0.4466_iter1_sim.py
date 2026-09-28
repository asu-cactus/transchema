import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_32/training_0.csv", index_col=0)
df0_selected = df0[['city', 'ride_id']].copy()
df0_selected['ride_id'] = df0_selected['ride_id'].astype(int)
df0_selected.to_csv("autopipeline-benchmarks/github-pipelines/length2_32/target_multisource_mcts.csv", index=False)