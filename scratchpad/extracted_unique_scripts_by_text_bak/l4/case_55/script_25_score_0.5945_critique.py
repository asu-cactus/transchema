import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv", index_col=0)

union_result = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Remove duplicates by grouping on WarNum and WhereFought without aggregation
result = union_result.drop_duplicates(subset=['WarNum', 'WhereFought']).copy()

result['WarNum'] = result['WarNum'].astype(int)
result['WhereFought'] = result['WhereFought'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)