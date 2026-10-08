import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

df = df0.copy()

# Group by 'Country / territory of asylum/residence' and sum 'Value'
df = df.groupby('Country / territory of asylum/residence', as_index=False).agg({'Value': 'sum'})

# Rename 'Value' to 'Year' to match target schema
df = df.rename(columns={'Value': 'Year'})

# Ensure 'Year' is integer type
df['Year'] = df['Year'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)