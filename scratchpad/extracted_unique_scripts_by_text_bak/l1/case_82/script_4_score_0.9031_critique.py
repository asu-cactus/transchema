import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

# Filter out rows where conservation_status is NaN, as target examples do not include NaN categories
df0_filtered = df0[df0['conservation_status'].notna()]

grouped = df0_filtered.groupby("conservation_status").agg(scientific_name=("scientific_name", "count")).reset_index()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)