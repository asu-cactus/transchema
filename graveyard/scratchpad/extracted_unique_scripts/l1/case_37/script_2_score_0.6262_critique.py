import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_37/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_37/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, how='outer', on=['business_id', 'date'])

merged = merged[['business_id', 'Score', 'date', 'type', 'ViolationTypeID', 'risk_category', 'description']]

merged['business_id'] = merged['business_id'].astype('Int64')
merged['Score'] = merged['Score'].astype(float)
merged['date'] = merged['date'].astype('Int64')
merged['type'] = merged['type'].astype(str)
merged['ViolationTypeID'] = merged['ViolationTypeID'].astype('Int64')
merged['risk_category'] = merged['risk_category'].astype(str)
merged['description'] = merged['description'].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_37/target_multisource_mcts.csv", index=False)