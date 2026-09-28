import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

agg_df = df.groupby(['PRECINCT', 'PARTY'], dropna=False).agg({
    'POLLS': 'sum',
    'EARLY_VOING': 'sum',
    'ABSENTEE': 'sum',
    'PROVISIONAL': 'sum',
    'ELIGIBLE_VOTERS': 'sum'
}).reset_index()

pivot_df = agg_df.pivot(index='PRECINCT', columns='PARTY', values=['POLLS', 'EARLY_VOING', 'ABSENTEE', 'PROVISIONAL', 'ELIGIBLE_VOTERS'])

pivot_df.columns = ['_'.join(col).strip() for col in pivot_df.columns.values]

sum_cols = ['POLLS_DEMOCRAT', 'POLLS_GREEN', 'POLLS_LIBERTARIAN',
            'EARLY_VOING_DEMOCRAT', 'EARLY_VOING_GREEN', 'EARLY_VOING_LIBERTARIAN',
            'ABSENTEE_DEMOCRAT', 'ABSENTEE_GREEN', 'ABSENTEE_LIBERTARIAN',
            'PROVISIONAL_DEMOCRAT', 'PROVISIONAL_GREEN', 'PROVISIONAL_LIBERTARIAN',
            'ELIGIBLE_VOTERS_DEMOCRAT', 'ELIGIBLE_VOTERS_GREEN', 'ELIGIBLE_VOTERS_LIBERTARIAN']

for col in sum_cols:
    if col not in pivot_df.columns:
        pivot_df[col] = 0

result = pd.DataFrame()
result['PRECINCT'] = pivot_df.index
result['POLLS'] = pivot_df[[c for c in pivot_df.columns if c.startswith('POLLS_')]].sum(axis=1).astype(int)
result['EARLY_VOING'] = pivot_df[[c for c in pivot_df.columns if c.startswith('EARLY_VOING_')]].sum(axis=1).astype(int)
result['ABSENTEE'] = pivot_df[[c for c in pivot_df.columns if c.startswith('ABSENTEE_')]].sum(axis=1).astype(int)
result['PROVISIONAL'] = pivot_df[[c for c in pivot_df.columns if c.startswith('PROVISIONAL_')]].sum(axis=1).astype(int)
result['ELIGIBLE_VOTERS'] = pivot_df[[c for c in pivot_df.columns if c.startswith('ELIGIBLE_VOTERS_')]].sum(axis=1).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)