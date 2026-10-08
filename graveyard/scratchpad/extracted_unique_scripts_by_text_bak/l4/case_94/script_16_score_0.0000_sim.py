import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

join1 = pd.merge(s0, s1, on=['Split','SubjectId','Subject'], suffixes=('_0','_1'))
join2 = pd.merge(join1, s2, on=['Split','SubjectId','Subject'])
final_join = pd.merge(join2, s3, on=['Split','SubjectId','Subject'], suffixes=('_2','_3'))

union_1_3 = pd.concat([s1, s3], ignore_index=True)

final_join.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)