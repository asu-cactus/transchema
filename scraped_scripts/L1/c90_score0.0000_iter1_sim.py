import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

joined = pd.merge(df, df, left_on='tweet_id', right_on='retweeted_status_id', how='inner', suffixes=('_left', '_right'))

def determine_dog_type(row):
    if pd.notna(row['doggo_left']) or pd.notna(row['floofer_left']) or pd.notna(row['pupper_left']) or pd.notna(row['puppo_left']):
        return 1
    if pd.notna(row['doggo_right']) or pd.notna(row['floofer_right']) or pd.notna(row['pupper_right']) or pd.notna(row['puppo_right']):
        return 1
    return 0

joined['dog_type'] = joined.apply(determine_dog_type, axis=1)

result = joined[['dog_type']].copy()
result['dog_type'] = result['dog_type'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv")