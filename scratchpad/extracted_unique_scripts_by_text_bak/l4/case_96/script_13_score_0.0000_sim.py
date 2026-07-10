import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

df0.columns = [f"{col}_0" if col not in ['SubjectId', 'Split', 'Subject'] else col for col in df0.columns]
df1.columns = [f"{col}_1" if col not in ['SubjectId', 'Split', 'Subject'] else col for col in df1.columns]
df2.columns = [f"{col}_2" if col not in ['SubjectId', 'Split', 'Subject'] else col for col in df2.columns]
df3.columns = [f"{col}_3" if col not in ['SubjectId', 'Split', 'Subject'] else col for col in df3.columns]

join_01 = pd.merge(df0, df1, on=['SubjectId', 'Split', 'Subject'], how='inner')
join_012 = pd.merge(join_01, df2, on=['SubjectId', 'Split', 'Subject'], how='inner')
join_0123 = pd.merge(join_012, df3, on=['SubjectId', 'Split', 'Subject'], how='inner')

agg_dict = {}
for suffix in ['_0', '_1', '_2', '_3']:
    for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
        agg_dict[f"{col}{suffix}"] = 'sum'

grouped = join_0123.groupby(['SubjectId', 'Split', 'Subject'], as_index=False).agg(agg_dict)

grouped['PA'] = grouped['PA_0'] + grouped['PA_1'] + grouped['PA_2'] + grouped['PA_3']
grouped['AB'] = grouped['AB_0'] + grouped['AB_1'] + grouped['AB_2'] + grouped['AB_3']
grouped['H'] = grouped['H_0'] + grouped['H_1'] + grouped['H_2'] + grouped['H_3']
grouped['TB'] = grouped['TB_0'] + grouped['TB_1'] + grouped['TB_2'] + grouped['TB_3']
grouped['BB'] = grouped['BB_0'] + grouped['BB_1'] + grouped['BB_2'] + grouped['BB_3']
grouped['SF'] = grouped['SF_0'] + grouped['SF_1'] + grouped['SF_2'] + grouped['SF_3']
grouped['HBP'] = grouped['HBP_0'] + grouped['HBP_1'] + grouped['HBP_2'] + grouped['HBP_3']

result = grouped[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

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