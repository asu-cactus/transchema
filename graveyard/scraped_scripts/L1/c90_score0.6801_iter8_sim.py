import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

def dog_stage(row):
    if row['doggo'] == 'doggo':
        return 4
    elif row['floofer'] == 'floofer':
        return 3
    elif row['pupper'] == 'pupper':
        return 2
    elif row['puppo'] == 'puppo':
        return 1
    else:
        return 0

df['dog_type'] = df.apply(dog_stage, axis=1)
result = df.groupby('dog_type').size().reset_index(name='count')
result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)