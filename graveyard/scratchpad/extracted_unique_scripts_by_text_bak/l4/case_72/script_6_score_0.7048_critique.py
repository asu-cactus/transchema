import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

# Aggregate Source4_72_0: mean fare by city
df0_agg = df0.groupby("city", as_index=False).agg({"fare": "mean"})

# Aggregate Source4_72_1: sum driver_count by city
df1_agg = df1.groupby("city", as_index=False).agg({"driver_count": "sum"})

# Join on city
df_joined = pd.merge(df0_agg, df1_agg, on="city", how="inner")

# Rename columns to match target schema
df_joined = df_joined.rename(columns={"fare": "a", "driver_count": "b"})

# Select final columns
df_result = df_joined[["city", "a", "b"]]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)