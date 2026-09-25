import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

joined = pd.merge(df, df, left_on='tweet_id', right_on='retweeted_status_id', suffixes=('_left', '_right'))

def extract_dog_type(row):
    for col in ['doggo_left', 'floofer_left', 'pupper_left', 'puppo_left',
                'doggo_right', 'floofer_right', 'pupper_right', 'puppo_right']:
        if pd.notna(row[col]) and row[col] != '':
            if 'doggo' in col:
                return 0
            elif 'floofer' in col:
                return 1
            elif 'pupper' in col:
                return 2
            elif 'puppo' in col:
                return 3
    return 4

joined['dog_type'] = joined.apply(extract_dog_type, axis=1)

result = joined.groupby('dog_type').size().reset_index(name='count')

result = result[['dog_type']]

result['dog_type'] = result['dog_type'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)