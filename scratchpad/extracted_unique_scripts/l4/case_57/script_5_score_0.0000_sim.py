import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

join_01 = pd.merge(df0, df1, on="WarNum", suffixes=('_0', '_1'))
join_012 = pd.merge(join_01, df2, on="WarNum")
join_0123 = pd.merge(join_012, df3, on="WarNum", suffixes=('', '_3'))

# Collect all TransTo columns from all sources
trans_to_cols = ['TransTo_0', 'TransTo_1', 'TransTo', 'TransTo_3']
join_0123.rename(columns={'TransTo_0': 'TransTo_0', 'TransTo_1': 'TransTo_1', 'TransTo': 'TransTo_2', 'TransTo_3': 'TransTo_3'}, inplace=True)

# Extract TransTo columns, stack them to one column, drop NaNs
trans_to_values = join_0123[['WarNum', 'TransTo_0', 'TransTo_1', 'TransTo_2', 'TransTo_3']].set_index('WarNum')
trans_to_long = trans_to_values.stack().reset_index(level=1, drop=True).reset_index()
trans_to_long.columns = ['WarNum', 'TransTo']
trans_to_long = trans_to_long.dropna(subset=['TransTo'])

# Group by TransTo and get WarNum (target schema: TransTo, WarNum)
result = trans_to_long.groupby('TransTo', as_index=False).agg({'WarNum': 'first'})

result = result[['TransTo', 'WarNum']].astype({'TransTo': 'Int64', 'WarNum': 'Int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)