import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, left_on=['Text Date', 'Value Date'], right_on=['Text Date', 'Value Date'], suffixes=('_left', '_right'))

df_result = pd.DataFrame()
df_result['Date'] = df_joined['Text Date']
df_result['Water Use'] = pd.to_numeric(df_joined['Water Use_left'], errors='coerce')
df_result['Power Use'] = pd.to_numeric(df_joined['Power Use_left'], errors='coerce').fillna(0).astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)