import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

def extract_dog_type(row):
    count = 0
    for col in ['doggo', 'floofer', 'pupper', 'puppo']:
        if pd.notna(row[col]) and row[col] != '':
            count += 1
    return count

df0['dog_type'] = df0.apply(extract_dog_type, axis=1)

result = df0.groupby('dog_type', as_index=False).size().rename(columns={'size': 'dog_type'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)