import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

joined_01 = pd.merge(df0, df1, on=['B-day', 'ID Number'], how='inner', suffixes=('_0', '_1'))
joined_all = pd.merge(joined_01, df2, on=['B-day', 'ID Number'], how='inner', suffixes=('', '_2'))

result = joined_all[['B-day', 'ID Number', 'Name', 'Fed', 'Sex']].copy()
result.rename(columns={
    'Name': 'Name_x',
    'Fed': 'Fed_x',
    'Sex': 'Sex_x'
}, inplace=True)

result = result.astype({
    'B-day': 'int64',
    'ID Number': 'int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)