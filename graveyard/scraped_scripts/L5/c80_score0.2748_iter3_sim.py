import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

pivot_df = df0.pivot(index='Purchase ID', columns='Item ID', values='Price').reset_index()
pivot_df.columns.name = None

merged = pivot_df.merge(df0, on=['Purchase ID'], how='inner', suffixes=('_x', '_y'))

merged['Purchase ID_x'] = merged['Purchase ID']
merged['Purchase ID_y'] = merged['Purchase ID']
merged['Age_x'] = merged['Age']
merged['Age_y'] = merged['Age']
merged['Item ID_x'] = merged['Item ID']
merged['Item ID_y'] = merged['Item ID']

cols = ['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID', 
        pivot_df.columns[1], 'Purchase ID_x', 'Age_x', 'Item ID_x', 
        pivot_df.columns[2] if len(pivot_df.columns) > 2 else None, 'Item ID_y', 'Purchase ID_y', 'Age_y']

cols = [c for c in cols if c in merged.columns]

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)