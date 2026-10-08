import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

# Drop rows with NaN in zipcode or AGI_STUB
df = df.dropna(subset=['zipcode', 'AGI_STUB'])

# Convert zipcode and AGI_STUB to int (if not already)
df['zipcode'] = df['zipcode'].astype(int)
df['AGI_STUB'] = df['AGI_STUB'].astype(int)

df_grouped = df.groupby(['zipcode', 'AGI_STUB'], as_index=False).agg({'N1':'sum', 'A00100':'sum'})

# Convert aggregated columns to int64
df_grouped = df_grouped.astype({'zipcode':'int64', 'AGI_STUB':'int64', 'N1':'int64', 'A00100':'int64'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)