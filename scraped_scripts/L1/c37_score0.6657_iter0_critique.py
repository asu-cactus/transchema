import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_37/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_37/training_1.csv", index_col=0)

# LEFT JOIN Source1_37_1 onto Source1_37_0 on business_id and date
merged = pd.merge(df0, df1, how='left', on=['business_id', 'date'])

# Select columns in target schema order
merged = merged[['business_id', 'Score', 'date', 'type', 'ViolationTypeID', 'risk_category', 'description']]

# Cast columns to target types
merged['business_id'] = merged['business_id'].astype('int64')
merged['Score'] = merged['Score'].astype('float64')
merged['date'] = merged['date'].astype('int64')
merged['type'] = merged['type'].astype('string')
merged['ViolationTypeID'] = merged['ViolationTypeID'].astype('Int64')  # Nullable integer because of left join
merged['risk_category'] = merged['risk_category'].astype('string')
merged['description'] = merged['description'].astype('string')

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_37/target_multisource_mcts.csv", index=False)