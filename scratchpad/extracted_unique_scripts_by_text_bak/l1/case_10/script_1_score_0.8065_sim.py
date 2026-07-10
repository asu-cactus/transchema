import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

agg = df.groupby(['PRECINCT', 'PARTY'], as_index=False).agg({
    'POLLS': 'sum',
    'EARLY_VOING': 'sum',
    'ABSENTEE': 'sum',
    'PROVISIONAL': 'sum',
    'ELIGIBLE_VOTERS': 'sum'
})

pivot = agg.pivot(index='PRECINCT', columns='PARTY', values=['POLLS', 'EARLY_VOING', 'ABSENTEE', 'PROVISIONAL', 'ELIGIBLE_VOTERS'])

pivot.columns = ['_'.join(col).upper() for col in pivot.columns]

pivot = pivot.reset_index()

cols = ['PRECINCT', 'ELIGIBLE_VOTERS_DEMOCRAT', 'POLLS_DEMOCRAT', 'EARLY_VOING_DEMOCRAT', 'ABSENTEE_DEMOCRAT', 'PROVISIONAL_DEMOCRAT']
if all(c in pivot.columns for c in cols[1:]):
    result = pivot[cols].copy()
else:
    # If DEMOCRAT columns missing, fill with 0
    for c in cols[1:]:
        if c not in pivot.columns:
            pivot[c] = 0
    result = pivot[cols].copy()

result = result.rename(columns={
    'ELIGIBLE_VOTERS_DEMOCRAT': 'ELIGIBLE_VOTERS',
    'POLLS_DEMOCRAT': 'POLLS',
    'EARLY_VOING_DEMOCRAT': 'EARLY_VOING',
    'ABSENTEE_DEMOCRAT': 'ABSENTEE',
    'PROVISIONAL_DEMOCRAT': 'PROVISIONAL'
})

result['ELIGIBLE_VOTERS'] = result['ELIGIBLE_VOTERS'].astype(int)
result['POLLS'] = result['POLLS'].astype(int)
result['EARLY_VOING'] = result['EARLY_VOING'].astype(int)
result['ABSENTEE'] = result['ABSENTEE'].astype(int)
result['PROVISIONAL'] = result['PROVISIONAL'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)