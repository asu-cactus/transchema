import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

joined = pd.merge(df, df, left_on='tweet_id', right_on='in_reply_to_status_id', suffixes=('_left', '_right'))

def get_dog_type(row):
    for col, val in [('doggo', row['doggo_left']), ('floofer', row['floofer_left']), ('pupper', row['pupper_left']), ('puppo', row['puppo_left'])]:
        if pd.notna(val) and val.strip() != '':
            if col == 'doggo':
                return 1
            elif col == 'floofer':
                return 3
            elif col == 'pupper':
                return 4
            elif col == 'puppo':
                return 8
    for col, val in [('doggo', row['doggo_right']), ('floofer', row['floofer_right']), ('pupper', row['pupper_right']), ('puppo', row['puppo_right'])]:
        if pd.notna(val) and val.strip() != '':
            if col == 'doggo':
                return 1
            elif col == 'floofer':
                return 3
            elif col == 'pupper':
                return 4
            elif col == 'puppo':
                return 8
    return 0

joined['dog_type'] = joined.apply(get_dog_type, axis=1)

result = joined.groupby('dog_type', as_index=False).size().rename(columns={'size':'count'})

result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)