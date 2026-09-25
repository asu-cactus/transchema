import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)  # County, r1403
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)  # County
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)  # County, r1402
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)  # County, r1401
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)  # County, r1403

# Start from s1 (dimension table with all counties)
df = s1.copy()

# Join s3 (r1401)
df = pd.merge(df, s3, on="County", how="left")

# Join s2 (r1402)
df = pd.merge(df, s2, on="County", how="left")

# Join s0 (r1403_x)
df = pd.merge(df, s0.rename(columns={"r1403": "r1403_x"}), on="County", how="left")

# Join s4 (r1403_y)
df = pd.merge(df, s4.rename(columns={"r1403": "r1403_y"}), on="County", how="left")

# Reorder columns to match target schema
df = df[['County', 'r1401', 'r1402', 'r1403_x', 'r1403_y']]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)