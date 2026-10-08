import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

def dog_type_from_row(row):
    if pd.notna(row['doggo']):
        return 3
    if pd.notna(row['floofer']):
        return 2
    if pd.notna(row['pupper']):
        return 4
    if pd.notna(row['puppo']):
        return 0
    return 0

df0['dog_type'] = df0.apply(dog_type_from_row, axis=1).astype(int)

# Group by dog_type and count occurrences
result = df0.groupby('dog_type').size().reset_index(name='dog_type')

# The target schema has only one column named 'dog_type' which holds counts

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)