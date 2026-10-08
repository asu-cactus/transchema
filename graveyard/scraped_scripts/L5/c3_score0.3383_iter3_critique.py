import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_5.csv", index_col=0)

# UNION Source5_3_3 and Source5_3_5 (same schema)
unioned_induction = pd.concat([s3, s5], ignore_index=True)

# Join unioned induction info with Source5_3_1
df = pd.merge(unioned_induction, s1, on="Artist", how="inner")

# Join with Source5_3_2
df = pd.merge(df, s2, on="Artist", how="inner")

# Join with Source5_3_4
df = pd.merge(df, s4, on="Artist", how="inner")

# Join with Source5_3_0
df = pd.merge(df, s0, on="Artist", how="inner")

# Convert columns to correct types
df["Year Inducted"] = pd.to_numeric(df["Year Inducted"], errors='coerce')
df["Years Waited"] = pd.to_numeric(df["Years Waited"], errors='coerce').astype('Int64')
df["# of Years Nominated"] = pd.to_numeric(df["# of Years Nominated"], errors='coerce').astype('Int64')
df["Certified Units (Millions)"] = pd.to_numeric(df["Certified Units (Millions)"], errors='coerce')
df["Influenced"] = pd.to_numeric(df["Influenced"], errors='coerce').astype('Int64')
df["Albums in RS500"] = pd.to_numeric(df["Albums in RS500"], errors='coerce').astype('Int64')
df["Top 100 Singles"] = pd.to_numeric(df["Top 100 Singles"], errors='coerce').astype('Int64')
df["Highest Position"] = pd.to_numeric(df["Highest Position"], errors='coerce').astype('Int64')

# Group by Artist to ensure unique rows (no aggregation needed as columns are unique per Artist)
df = df.groupby("Artist", as_index=False).first()

# Select target columns in order
target_cols = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
               'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position']

df_target = df[target_cols]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length5_3/target_multisource_mcts.csv", index=False)