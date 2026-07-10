import pandas as pd

# Read the four large tables with the same schema
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_4.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_8.csv", index_col=0)

# Union these four tables
unioned = pd.concat([s2, s3, s4, s8], ignore_index=True)

# Read other tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_1.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_7.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_9.csv", index_col=0)

# Join unioned with s0 on ROW_WID
df = unioned.merge(s0, on='ROW_WID', how='inner')

# Join with s1
df = df.merge(s1, on='ROW_WID', how='inner')

# Join with s5
df = df.merge(s5, on='ROW_WID', how='inner')

# Join with s6
df = df.merge(s6, on='ROW_WID', how='inner')

# Join with s7
df = df.merge(s7, on='ROW_WID', how='inner')

# Join with s9
df = df.merge(s9, on='ROW_WID', how='inner')

# Project CANCEL_DT
result = df[['CANCEL_DT']].copy()

# Convert CANCEL_DT to string and replace 'nan' string with pd.NA
result['CANCEL_DT'] = result['CANCEL_DT'].astype(str)
result.loc[result['CANCEL_DT'] == 'nan', 'CANCEL_DT'] = pd.NA

# Group by CANCEL_DT to remove duplicates
result = result.groupby('CANCEL_DT', dropna=False).size().reset_index()[['CANCEL_DT']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_26/target_multisource_mcts.csv", index=False)