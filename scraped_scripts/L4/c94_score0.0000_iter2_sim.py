import pandas as pd

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

merged = pd.merge(s2, s3, on=["SubjectId", "Split"], suffixes=('_2', '_3'))

agg_cols = ['Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

def to_int_safe(x):
    try:
        return int(x)
    except:
        return pd.NA

merged['Subject_2'] = merged['Subject_2'].apply(to_int_safe)
merged['Subject_3'] = merged['Subject_3'].apply(to_int_safe)

merged['Subject'] = merged[['Subject_2', 'Subject_3']].bfill(axis=1).iloc[:, 0]

agg_dict = {
    'Subject': 'first',
    'PA_2': 'sum',
    'AB_2': 'sum',
    'H_2': 'sum',
    'TB_2': 'sum',
    'BB_2': 'sum',
    'SF_2': 'sum',
    'HBP_2': 'sum',
    'PA_3': 'sum',
    'AB_3': 'sum',
    'H_3': 'sum',
    'TB_3': 'sum',
    'BB_3': 'sum',
    'SF_3': 'sum',
    'HBP_3': 'sum',
}

grouped = merged.groupby(['Split', 'SubjectId']).agg(agg_dict).reset_index()

grouped['PA'] = grouped['PA_2'] + grouped['PA_3']
grouped['AB'] = grouped['AB_2'] + grouped['AB_3']
grouped['H'] = grouped['H_2'] + grouped['H_3']
grouped['TB'] = grouped['TB_2'] + grouped['TB_3']
grouped['BB'] = grouped['BB_2'] + grouped['BB_3']
grouped['SF'] = grouped['SF_2'] + grouped['SF_3']
grouped['HBP'] = grouped['HBP_2'] + grouped['HBP_3']

result = grouped[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

result['SubjectId'] = result['SubjectId'].astype('Int64')
result['Subject'] = result['Subject'].astype('Int64')
for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    result[col] = result[col].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)