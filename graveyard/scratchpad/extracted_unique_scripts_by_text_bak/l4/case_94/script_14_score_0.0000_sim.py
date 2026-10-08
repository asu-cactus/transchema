import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

agg0 = df0.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})
agg1 = df1.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})
agg2 = df2.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})
agg3 = df3.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})

join_01 = pd.merge(agg0, agg1, on=['Split', 'SubjectId', 'Subject'], suffixes=('_0', '_1'))
join_01['PA'] = join_01['PA_0'] + join_01['PA_1']
join_01['AB'] = join_01['AB_0'] + join_01['AB_1']
join_01['H'] = join_01['H_0'] + join_01['H_1']
join_01['TB'] = join_01['TB_0'] + join_01['TB_1']
join_01['BB'] = join_01['BB_0'] + join_01['BB_1']
join_01['SF'] = join_01['SF_0'] + join_01['SF_1']
join_01['HBP'] = join_01['HBP_0'] + join_01['HBP_1']
join_01 = join_01[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

join_012 = pd.merge(join_01, agg2, on=['Split', 'SubjectId', 'Subject'], suffixes=('', '_2'))
join_012['PA'] += join_012['PA_2']
join_012['AB'] += join_012['AB_2']
join_012['H'] += join_012['H_2']
join_012['TB'] += join_012['TB_2']
join_012['BB'] += join_012['BB_2']
join_012['SF'] += join_012['SF_2']
join_012['HBP'] += join_012['HBP_2']
join_012 = join_012[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

join_0123 = pd.merge(join_012, agg3, on=['Split', 'SubjectId', 'Subject'], suffixes=('', '_3'))
join_0123['PA'] += join_0123['PA_3']
join_0123['AB'] += join_0123['AB_3']
join_0123['H'] += join_0123['H_3']
join_0123['TB'] += join_0123['TB_3']
join_0123['BB'] += join_0123['BB_3']
join_0123['SF'] += join_0123['SF_3']
join_0123['HBP'] += join_0123['HBP_3']
join_0123 = join_0123[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

join_0123['SubjectId'] = join_0123['SubjectId'].astype(int)
join_0123['Subject'] = join_0123['Subject'].astype(int)

join_0123.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)