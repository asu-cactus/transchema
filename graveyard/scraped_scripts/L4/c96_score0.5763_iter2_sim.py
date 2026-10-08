import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

df0_renamed = df0.rename(columns=lambda x: x if x in ['SubjectId', 'Split', 'Subject'] else f"{x}_0")
df1_renamed = df1.rename(columns=lambda x: x if x in ['SubjectId', 'Split', 'Subject'] else f"{x}_1")
df2_renamed = df2.rename(columns=lambda x: x if x in ['SubjectId', 'Split', 'Subject'] else f"{x}_2")
df3_renamed = df3.rename(columns=lambda x: x if x in ['SubjectId', 'Split', 'Subject'] else f"{x}_3")

join_01 = pd.merge(df0_renamed, df1_renamed, on=['SubjectId', 'Split', 'Subject'], how='outer')
join_012 = pd.merge(join_01, df2_renamed, on=['SubjectId', 'Split', 'Subject'], how='outer')
join_0123 = pd.merge(join_012, df3_renamed, on=['SubjectId', 'Split', 'Subject'], how='outer')

agg_dict = {}
for suffix in ['_0', '_1', '_2', '_3']:
    for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
        agg_dict[f"{col}{suffix}"] = 'sum'

grouped = join_0123.groupby(['SubjectId', 'Split', 'Subject'], dropna=False).agg(agg_dict).reset_index()

grouped['PA'] = grouped[[f"PA{i}" for i in ['_0','_1','_2','_3']]].sum(axis=1)
grouped['AB'] = grouped[[f"AB{i}" for i in ['_0','_1','_2','_3']]].sum(axis=1)
grouped['H'] = grouped[[f"H{i}" for i in ['_0','_1','_2','_3']]].sum(axis=1)
grouped['TB'] = grouped[[f"TB{i}" for i in ['_0','_1','_2','_3']]].sum(axis=1)
grouped['BB'] = grouped[[f"BB{i}" for i in ['_0','_1','_2','_3']]].sum(axis=1)
grouped['SF'] = grouped[[f"SF{i}" for i in ['_0','_1','_2','_3']]].sum(axis=1)
grouped['HBP'] = grouped[[f"HBP{i}" for i in ['_0','_1','_2','_3']]].sum(axis=1)

result = grouped[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

result['SubjectId'] = result['SubjectId'].astype('Int64')
result['Split'] = result['Split'].astype('Int64', errors='ignore')
result['Subject'] = result['Subject'].astype('Int64', errors='ignore')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)