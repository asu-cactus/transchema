import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

# UNION all source tables
union_all = pd.concat([s0, s1, s2, s3, s4], ignore_index=True, sort=False)

# GROUP BY hero
result = union_all.groupby("hero", as_index=False).agg({
    'disadvantage': 'mean',  # simple mean as per Hint 16
    'winrate': 'mean',       # simple mean as per Hint 16
    'matches': 'sum'         # sum matches as count
})

# Ensure correct dtypes
result['hero'] = result['hero'].astype(str)
result['disadvantage'] = result['disadvantage'].astype(float)
result['winrate'] = result['winrate'].astype(float)
result['matches'] = result['matches'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)