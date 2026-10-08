import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

dog_cols = ['doggo', 'floofer', 'pupper', 'puppo']

def dog_type_value(row):
    for i, col in enumerate(dog_cols):
        if pd.notna(row[col]) and row[col].strip() != '':
            return i + 1
    return 0

df['dog_type'] = df.apply(dog_type_value, axis=1)

result = df.groupby('dog_type').size().reset_index(name='dog_type')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)