import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

# Rename columns to standard schema
for df in [s0, s1, s2, s3]:
    df.columns = ['x', 'y', 'label']

# Union all source tables
result = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Convert types according to target schema: y float, x int, label int (from categorical codes)
result['y'] = result['y'].astype(float)
result['x'] = pd.to_numeric(result['x'], errors='coerce').astype('Int64')
result['label'] = result['label'].astype('category').cat.codes.astype('Int64')

result = result[['y', 'x', 'label']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)