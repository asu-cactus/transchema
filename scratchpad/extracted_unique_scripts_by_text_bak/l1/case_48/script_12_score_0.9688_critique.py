import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming all source files are named similarly)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_48/training_*.csv"
files = sorted(glob.glob(file_pattern))

dfs = []
for f in files:
    df = pd.read_csv(f, index_col=0)
    # Extract only needed columns and rename 'Text Date' to 'Date'
    df = df[['Text Date', 'Water Use', 'Power Use']].copy()
    df.rename(columns={'Text Date': 'Date'}, inplace=True)
    # Convert types as per target schema
    df['Water Use'] = df['Water Use'].astype(float)
    df['Power Use'] = df['Power Use'].astype(int)
    dfs.append(df)

# UNION all source tables by concatenation
df_all = pd.concat(dfs, ignore_index=True)

# GROUP BY 'Date' and aggregate sums of 'Water Use' and 'Power Use'
df_grouped = df_all.groupby('Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})

# Write to target CSV
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)