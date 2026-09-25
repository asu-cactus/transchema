import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

def extract_dog_type(row):
    if pd.notna(row['doggo']):
        return 1
    if pd.notna(row['floofer']):
        return 2
    if pd.notna(row['pupper']):
        return 3
    if pd.notna(row['puppo']):
        return 4
    return 0

df0['dog_type'] = df0.apply(extract_dog_type, axis=1)

# Group by dog_type and count number of tweets per dog_type
result = df0.groupby('dog_type', as_index=False).agg({'tweet_id': 'count'})

# Rename count column to dog_type to match target schema
result = result.rename(columns={'tweet_id': 'dog_type'})

# Keep only the dog_type column (which now contains counts)
result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)