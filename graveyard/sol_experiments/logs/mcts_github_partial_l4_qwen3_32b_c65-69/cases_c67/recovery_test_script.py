import pandas as pd

df_source = pd.read_csv(
    'autopipeline-benchmarks/github-pipelines/length4_67/test_0.csv',
    index_col=0
)

df_source['overs'] = df_source['overs'].astype(float)
df_source['runs scored'] = df_source['runs scored'].astype(int)
df_source['extras'] = df_source['extras'].fillna(0).astype(int)

grouped = df_source.groupby('Batsman on strike', as_index=False).agg({
    'overs': 'sum',
    'runs scored': 'sum',
    'extras': 'sum'
})

grouped.to_csv(
    'autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts_recovery_test_val.csv', 
    index=False
)