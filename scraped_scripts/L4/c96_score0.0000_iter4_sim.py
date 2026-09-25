import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

join_2_3 = pd.merge(s2, s3, on=["SubjectId", "Split", "Subject"], suffixes=('_2', '_3'))

union_0_1 = pd.concat([s0, s1], ignore_index=True)

final_join = pd.merge(union_0_1, join_2_3, on=["SubjectId", "Split", "Subject"])

agg = final_join.groupby(["SubjectId", "Split", "Subject"], as_index=False).agg({
    'PA_2': 'sum', 'PA_3': 'sum', 'PA': 'sum',
    'AB_2': 'sum', 'AB_3': 'sum', 'AB': 'sum',
    'H_2': 'sum', 'H_3': 'sum', 'H': 'sum',
    'TB_2': 'sum', 'TB_3': 'sum', 'TB': 'sum',
    'BB_2': 'sum', 'BB_3': 'sum', 'BB': 'sum',
    'SF_2': 'sum', 'SF_3': 'sum', 'SF': 'sum',
    'HBP_2': 'sum', 'HBP_3': 'sum', 'HBP': 'sum'
})

agg['PA'] = agg['PA'] + agg['PA_2'] + agg['PA_3']
agg['AB'] = agg['AB'] + agg['AB_2'] + agg['AB_3']
agg['H'] = agg['H'] + agg['H_2'] + agg['H_3']
agg['TB'] = agg['TB'] + agg['TB_2'] + agg['TB_3']
agg['BB'] = agg['BB'] + agg['BB_2'] + agg['BB_3']
agg['SF'] = agg['SF'] + agg['SF_2'] + agg['SF_3']
agg['HBP'] = agg['HBP'] + agg['HBP_2'] + agg['HBP_3']

result = agg[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

result['SubjectId'] = result['SubjectId'].astype(int)
result['Split'] = result['Split'].astype(int)
result['Subject'] = result['Subject'].astype(int)
result['PA'] = result['PA'].astype(int)
result['AB'] = result['AB'].astype(int)
result['H'] = result['H'].astype(int)
result['TB'] = result['TB'].astype(int)
result['BB'] = result['BB'].astype(int)
result['SF'] = result['SF'].astype(int)
result['HBP'] = result['HBP'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)