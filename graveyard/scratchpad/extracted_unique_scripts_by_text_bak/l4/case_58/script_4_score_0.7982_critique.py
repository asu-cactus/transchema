import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
union_all = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Drop duplicates on WarNum to get unique keys
unique_warnum = union_all.drop_duplicates(subset=['WarNum'])[['WarNum']]

# Set TransTo to 0 as per target examples
result = unique_warnum.copy()
result['TransTo'] = 0

# Ensure correct types
result['WarNum'] = result['WarNum'].astype(int)
result['TransTo'] = result['TransTo'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)