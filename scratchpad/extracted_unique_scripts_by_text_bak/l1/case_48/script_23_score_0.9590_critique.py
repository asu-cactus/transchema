import pandas as pd

# Read the single source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

# Group by 'Value Date' and sum 'Water Use' and 'Power Use'
agg = df0.groupby("Value Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

# Rename 'Value Date' to 'Date' to match target schema
agg = agg.rename(columns={"Value Date": "Date"})

# Ensure correct types
agg["Date"] = agg["Date"].astype(str)
agg["Water Use"] = agg["Water Use"].astype(float)
agg["Power Use"] = agg["Power Use"].astype(int)

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)