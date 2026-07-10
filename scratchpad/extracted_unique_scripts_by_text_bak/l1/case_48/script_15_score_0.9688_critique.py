import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

# Select relevant columns and rename 'Text Date' to 'Date'
df0 = df0[['Text Date', 'Water Use', 'Power Use']].rename(columns={'Text Date': 'Date'})

# Convert types explicitly
df0['Water Use'] = df0['Water Use'].astype(float)
df0['Power Use'] = df0['Power Use'].astype(int)

# Group by 'Date' and sum the usage columns
df_agg = df0.groupby('Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})

# Write output
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)