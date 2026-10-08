import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

def get_dog_type(row):
    if pd.notna(row['doggo']):
        return 4
    if pd.notna(row['floofer']):
        return 3
    if pd.notna(row['pupper']):
        return 8
    if pd.notna(row['puppo']):
        return 0
    return None

df0['dog_type'] = df0.apply(get_dog_type, axis=1)
result = df0.groupby('dog_type').size().reset_index(name='count')
result = result[['dog_type']].dropna().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)