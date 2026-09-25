import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv", index_col=0)

j01 = pd.merge(s0, s1, on=['WarNum', 'WhereFought'])
j012 = pd.merge(j01, s2, on=['WarNum', 'WhereFought'])
j0123 = pd.merge(j012, s3, on=['WarNum', 'WhereFought'])

pivoted = j0123.pivot(index='WhereFought', columns='WarNum', values='WarNum')
pivoted = pivoted.reset_index()

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)