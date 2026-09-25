import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on='school_name', how='inner')

agg = merged.groupby(['school_name', 'type'], as_index=False).agg({
    'size': 'max',
    'budget': 'max',
    'reading_score': 'mean',
    'math_score': 'mean'
})

agg = agg.rename(columns={
    'type': 'a',
    'size': 'b',
    'budget': 'c',
    'reading_score': 'd',
    'math_score': 'e'
})

agg['b'] = agg['b'].astype(int)
agg['c'] = agg['c'].astype(int)
agg['d'] = agg['d'].astype(float)
agg['e'] = agg['e'].astype(float)

result = agg[['school_name', 'a', 'b', 'c', 'd', 'e']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)