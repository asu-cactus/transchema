import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

agg0 = df0.groupby(['Split', 'SubjectId'], as_index=False).agg({
    'PA': 'min',
    'AB': 'min',
    'H': 'min',
    'TB': 'min',
    'BB': 'min',
    'SF': 'min',
    'HBP': 'min'
})

union_df = pd.concat([agg0, df1, df2, df3], ignore_index=True)

result = union_df.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA': 'min',
    'AB': 'min',
    'H': 'min',
    'TB': 'min',
    'BB': 'min',
    'SF': 'min',
    'HBP': 'min'
})

result['Split'] = result['Split'].astype(str)
result['SubjectId'] = result['SubjectId'].astype(int)
result['Subject'] = result['Subject'].apply(lambda x: int(x) if str(x).isdigit() else x)
if result['Subject'].dtype != 'int64':
    # Try to convert Subject to int if possible, else leave as is
    try:
        result['Subject'] = result['Subject'].astype(int)
    except:
        pass

result = result[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)