import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_10/test_0.csv', index_col=0)
df = df[['PRECINCT', 'POLLS', 'EARLY_VOING', 'ABSENTEE', 'PROVISIONAL', 'ELIGIBLE_VOTERS']]
grouped = df.groupby('PRECINCT').sum().reset_index()
grouped = grouped[['PRECINCT', 'ELIGIBLE_VOTERS', 'POLLS', 'EARLY_VOING', 'ABSENTEE', 'PROVISIONAL']]
grouped = grouped.astype({
    'ELIGIBLE_VOTERS': 'int',
    'POLLS': 'int',
    'EARLY_VOING': 'int',
    'ABSENTEE': 'int',
    'PROVISIONAL': 'int'
})
grouped.to_csv('autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts_recovery_test_val.csv', index=False)