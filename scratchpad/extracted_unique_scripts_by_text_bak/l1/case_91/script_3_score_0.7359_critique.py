import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

# Lowercase the 'Name' column to match target examples
df['Name'] = df['Name'].str.lower()

# Ensure types match target schema
df['Age'] = df['Age'].astype(int)
df['Transfer_fee'] = df['Transfer_fee'].astype('Int64')  # allow NA integers
df['Market_value'] = df['Market_value'].astype(float)

# Output the dataframe as is, no aggregation or group by needed
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)