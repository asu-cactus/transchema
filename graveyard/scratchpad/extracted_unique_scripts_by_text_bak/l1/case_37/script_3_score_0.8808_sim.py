import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length1_37/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length1_37/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_37/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

grouped = df0.groupby(['business_id', 'date', 'type'], as_index=False)['Score'].mean()

merged = pd.merge(grouped, df1, on=['business_id', 'date'], how='inner')

merged = merged[['business_id', 'Score', 'date', 'type', 'ViolationTypeID', 'risk_category', 'description']]

merged['business_id'] = merged['business_id'].astype(int)
merged['Score'] = merged['Score'].astype(float)
merged['date'] = merged['date'].astype(int)
merged['type'] = merged['type'].astype(str)
merged['ViolationTypeID'] = merged['ViolationTypeID'].astype(int)
merged['risk_category'] = merged['risk_category'].astype(str)
merged['description'] = merged['description'].astype(str)

merged.to_csv(target_path, index=False)