import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

union_0_1 = pd.concat([s0, s1], ignore_index=True)

join_2_3 = pd.merge(s2, s3, on=['SubjectId', 'Split', 'Subject'], suffixes=('_2', '_3'))

cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']
for c in cols:
    join_2_3[c] = join_2_3[c + '_2'].fillna(0).astype(int) + join_2_3[c + '_3'].fillna(0).astype(int)

join_2_3 = join_2_3[['SubjectId', 'Split', 'Subject'] + cols]

final = pd.merge(union_0_1, join_2_3, on=['SubjectId', 'Split', 'Subject'], suffixes=('_u', '_j'))

for c in cols:
    final[c] = final[c + '_u'].fillna(0).astype(int) + final[c + '_j'].fillna(0).astype(int)

final = final[['SubjectId', 'Split', 'Subject'] + cols]

final['SubjectId'] = final['SubjectId'].astype(int)
final['Split'] = final['Split'].astype(int)
final['Subject'] = final['Subject'].astype(int)
for c in cols:
    final[c] = final[c].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)