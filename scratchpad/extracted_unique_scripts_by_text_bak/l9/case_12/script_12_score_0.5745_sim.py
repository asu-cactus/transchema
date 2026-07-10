import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_9.csv", index_col=0)
df10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_10.csv", index_col=0)

pivot_df0 = df0.pivot_table(index='2012-12-05', values='301.0', aggfunc='sum').reset_index()

join1 = pd.merge(pivot_df0, df1, on='2012-12-05', how='outer')
join2 = pd.merge(join1, df2, on='2012-12-05', how='outer')
join3 = pd.merge(join2, df3, on='2012-12-05', how='outer')
join4 = pd.merge(join3, df4, on='2012-12-05', how='outer')
join5 = pd.merge(join4, df5, on='2012-12-05', how='outer')
join6 = pd.merge(join5, df6, on='2012-12-05', how='outer')
join7 = pd.merge(join6, df7, on='2012-12-05', how='outer')
join8 = pd.merge(join7, df8, on='2012-12-05', how='outer')
join9 = pd.merge(join8, df9, on='2012-12-05', how='outer')
final_df = pd.merge(join9, df10, on='2012-12-05', how='outer')

final_df = final_df.astype({
    '2012-12-05': str,
    '301.0': 'Int64',
    '0.0075805085': 'float',
    '0.0179': 'float',
    '6.9': 'float',
    '0.17657143': 'float',
    '20.3333': 'float',
    '0.016157143': 'float',
    '242.364': 'float',
    '0.1646': 'float',
    '0.7268': 'float',
    '0.4332': 'float'
})

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)