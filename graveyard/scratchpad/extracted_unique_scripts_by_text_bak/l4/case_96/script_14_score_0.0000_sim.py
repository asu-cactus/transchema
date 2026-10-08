import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

join_2_3 = pd.merge(s2, s3, on=['SubjectId', 'Split', 'Subject'], suffixes=('_2', '_3'))

union_0_1 = pd.concat([s0, s1], ignore_index=True)

final = pd.merge(union_0_1, join_2_3, on=['SubjectId', 'Split', 'Subject'], how='inner')

cols = ['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

final = final[cols]

final['SubjectId'] = final['SubjectId'].astype(int)
final['Split'] = final['Split'].astype(int)
final['Subject'] = final['Subject'].astype(int)
for c in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    final[c] = final[c].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)