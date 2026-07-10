import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

# Start from Source1 (County only) to restrict Counties
result = source1

# Join with Source2 (County, m1401)
result = result.merge(source2, on='County', how='left')

# Join with Source3 (County, m1402)
result = result.merge(source3, on='County', how='left')

# Join with Source0 (County, m1403)
result = result.merge(source0, on='County', how='left')

# Join with Source4 (County, m1404)
result = result.merge(source4, on='County', how='left')

# Reorder columns to match target schema
result = result[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)