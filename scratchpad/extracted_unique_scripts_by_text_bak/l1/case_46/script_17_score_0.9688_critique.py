import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files exist)
# Since only one source file is given, this will read just that one.
file_paths = ["autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv"]

# If multiple source files existed, e.g., training_0.csv, training_1.csv, etc., we would do:
# file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_46/training_*.csv")

dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]

# UNION all source tables (concatenate)
df_all = pd.concat(dfs, ignore_index=True)

# GROUP BY 'Text Date' and aggregate sums of 'Water Use' and 'Power Use'
agg = df_all.groupby('Text Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})

# Rename 'Text Date' to 'Date' to match target schema
agg = agg.rename(columns={'Text Date': 'Date'})

# Cast columns to correct types as per target schema
agg['Date'] = agg['Date'].astype(str)
agg['Water Use'] = agg['Water Use'].astype(float)
agg['Power Use'] = agg['Power Use'].astype(int)

# Write output to target file
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)