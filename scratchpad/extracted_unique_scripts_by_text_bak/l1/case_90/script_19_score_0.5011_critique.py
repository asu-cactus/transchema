import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

df['doggo'] = df['doggo'].fillna('')
df['floofer'] = df['floofer'].fillna('')
df['pupper'] = df['pupper'].fillna('')
df['puppo'] = df['puppo'].fillna('')

def dog_type(row):
    if row['doggo'] == 'doggo':
        return 2
    elif row['floofer'] == 'floofer':
        return 3
    elif row['pupper'] == 'pupper':
        return 1
    elif row['puppo'] == 'puppo':
        return 4
    else:
        return 0

df['dog_type'] = df.apply(dog_type, axis=1)

result = df.groupby('dog_type').agg({'tweet_id': 'count'}).reset_index()
result = result.rename(columns={'tweet_id': 'dog_type_count'})

expanded_rows = []
for _, row in result.iterrows():
    expanded_rows.extend([row['dog_type']] * row['dog_type_count'])

final_df = pd.DataFrame({'dog_type': expanded_rows})

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)