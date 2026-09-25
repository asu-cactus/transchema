import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

df_grouped = df.groupby(['doggo', 'floofer', 'pupper', 'puppo'], dropna=False).agg({'tweet_id':'count'}).reset_index()

def dog_type_value(row):
    if pd.notna(row['doggo']):
        return 1
    if pd.notna(row['floofer']):
        return 10
    if pd.notna(row['pupper']):
        return 100
    if pd.notna(row['puppo']):
        return 1000
    return 0

df_grouped['dog_type'] = df_grouped.apply(dog_type_value, axis=1)

result = df_grouped.groupby('dog_type', dropna=False)['tweet_id'].sum().reset_index()

result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)