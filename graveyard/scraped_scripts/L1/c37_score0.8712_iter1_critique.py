import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_37/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_37/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on=["business_id", "date"], how="left")

df = df[['business_id', 'Score', 'date', 'type', 'ViolationTypeID', 'risk_category', 'description']]

df = df.dropna(subset=['ViolationTypeID', 'risk_category', 'description'])

df['business_id'] = df['business_id'].astype(int)
df['Score'] = df['Score'].astype(float)
df['date'] = df['date'].astype(int)
df['type'] = df['type'].astype(str)
df['ViolationTypeID'] = df['ViolationTypeID'].astype(int)
df['risk_category'] = df['risk_category'].astype(str)
df['description'] = df['description'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_37/target_multisource_mcts.csv", index=False)