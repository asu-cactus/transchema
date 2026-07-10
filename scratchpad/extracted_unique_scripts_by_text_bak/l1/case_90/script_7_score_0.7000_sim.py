import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

dog_cols = ['doggo', 'floofer', 'pupper', 'puppo']
df_dogs = df[['tweet_id'] + dog_cols].copy()

def dog_type_value(row):
    for i, col in enumerate(dog_cols):
        if pd.notna(row[col]) and row[col].strip() != '':
            return i + 1
    return 0

df_dogs['dog_type'] = df_dogs.apply(dog_type_value, axis=1)

result = df_dogs.groupby('dog_type').size().reset_index(name='count')

result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)