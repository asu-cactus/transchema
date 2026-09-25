import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv", index_col=0)

union_result = pd.concat([df0, df1, df2, df3], ignore_index=True)

grouped = union_result.groupby(['WarNum', 'WhereFought'], as_index=False).size()

grouped.columns = ['WarNum', 'WhereFought', 'Count']

result = grouped[['WarNum', 'WhereFought']].astype({'WarNum': 'int64', 'WhereFought': 'int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)