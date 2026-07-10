import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_2/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_2/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df = df.astype({
    'tripduration': 'int64',
    'starttime': 'string',
    'stoptime': 'string',
    'start station id': 'int64',
    'start station name': 'string',
    'start station latitude': 'float64',
    'start station longitude': 'float64',
    'end station id': 'int64',
    'end station name': 'string',
    'end station latitude': 'float64',
    'end station longitude': 'float64',
    'bikeid': 'int64',
    'usertype': 'string',
    'birth year': 'Int64',
    'gender': 'Int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_2/target_multisource_mcts.csv", index=False)