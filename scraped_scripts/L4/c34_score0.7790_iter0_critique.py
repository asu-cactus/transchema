import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)

# Rename columns to match target schema before join
df0 = df0.rename(columns={"batsman_runs": "batsman_runs_x"})
df3 = df3.rename(columns={"batsman_runs": "batsman_runs_y"})
df1 = df1.rename(columns={"total_runs": "total_runs_x"})
df4 = df4.rename(columns={"total_runs": "total_runs_y"})

# Join all tables on 'batsman' using inner join to get 258 rows
merged = df1.merge(df4, on="batsman", how="inner") \
            .merge(df0, on="batsman", how="inner") \
            .merge(df3, on="batsman", how="inner") \
            .merge(df2, on="batsman", how="inner")

# Ensure correct dtypes
merged["total_runs_x"] = merged["total_runs_x"].astype(int)
merged["total_runs_y"] = merged["total_runs_y"].astype(int)
merged["batsman_runs_x"] = merged["batsman_runs_x"].astype(int)
merged["batsman_runs_y"] = merged["batsman_runs_y"].astype(int)
merged["no of balls"] = merged["no of balls"].astype(int)
merged["batsman_runs"] = merged["batsman_runs"].astype(int)
merged["strike"] = merged["strike"].astype(float)

# Select columns in target order
merged = merged[["batsman", "total_runs_x", "batsman_runs_x", "batsman_runs_y", "no of balls", "batsman_runs", "strike", "total_runs_y"]]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)