import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_22/training_1.csv", index_col=0)

df0_sel = df0[['city', 'ride_id']]
df1_sel = df1[['city']].copy()
df1_sel['ride_id'] = pd.NA

result = pd.concat([df0_sel, df1_sel], ignore_index=True)
result = result[['city', 'ride_id']]
result['ride_id'] = pd.to_numeric(result['ride_id'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_22/target_multisource_mcts.csv", index=False)