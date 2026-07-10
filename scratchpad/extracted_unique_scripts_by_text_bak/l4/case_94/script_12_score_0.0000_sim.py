import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

join_0_1 = pd.merge(df0, df1, on=['SubjectId', 'Split'], suffixes=('_0', '_1'))
join_0_1_2 = pd.merge(join_0_1, df2, on=['SubjectId', 'Split'], suffixes=('', '_2'))
join_0_1_2_3 = pd.merge(join_0_1_2, df3, on=['SubjectId', 'Split'], suffixes=('', '_3'))

agg_df = join_0_1_2_3.groupby(['Split', 'SubjectId', 'Subject_0'], as_index=False).agg({
    'PA_0': 'sum', 'PA_1': 'sum', 'PA': 'sum', 'PA_3': 'sum',
    'AB_0': 'sum', 'AB_1': 'sum', 'AB': 'sum', 'AB_3': 'sum',
    'H_0': 'sum', 'H_1': 'sum', 'H': 'sum', 'H_3': 'sum',
    'TB_0': 'sum', 'TB_1': 'sum', 'TB': 'sum', 'TB_3': 'sum',
    'BB_0': 'sum', 'BB_1': 'sum', 'BB': 'sum', 'BB_3': 'sum',
    'SF_0': 'sum', 'SF_1': 'sum', 'SF': 'sum', 'SF_3': 'sum',
    'HBP_0': 'sum', 'HBP_1': 'sum', 'HBP': 'sum', 'HBP_3': 'sum'
})

agg_df['PA'] = agg_df['PA_0'] + agg_df['PA_1'] + agg_df['PA'] + agg_df['PA_3']
agg_df['AB'] = agg_df['AB_0'] + agg_df['AB_1'] + agg_df['AB'] + agg_df['AB_3']
agg_df['H'] = agg_df['H_0'] + agg_df['H_1'] + agg_df['H'] + agg_df['H_3']
agg_df['TB'] = agg_df['TB_0'] + agg_df['TB_1'] + agg_df['TB'] + agg_df['TB_3']
agg_df['BB'] = agg_df['BB_0'] + agg_df['BB_1'] + agg_df['BB'] + agg_df['BB_3']
agg_df['SF'] = agg_df['SF_0'] + agg_df['SF_1'] + agg_df['SF'] + agg_df['SF_3']
agg_df['HBP'] = agg_df['HBP_0'] + agg_df['HBP_1'] + agg_df['HBP'] + agg_df['HBP_3']

result = agg_df[['Split', 'SubjectId', 'Subject_0', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']].copy()
result.rename(columns={'Subject_0': 'Subject'}, inplace=True)
result = result.astype({
    'Split': str,
    'SubjectId': int,
    'Subject': int,
    'PA': int,
    'AB': int,
    'H': int,
    'TB': int,
    'BB': int,
    'SF': int,
    'HBP': int
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)