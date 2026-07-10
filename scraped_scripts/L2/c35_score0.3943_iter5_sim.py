import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_35/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_35/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_35/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df0['ResultDir'] = pd.to_numeric(df0['ResultDir'], errors='coerce')
df0['Date'] = df0['Date'].astype(str)

pivoted_source0 = df0.groupby('Date', as_index=False)['ResultDir'].mean()

df1['NumMosquitos'] = pd.to_numeric(df1['NumMosquitos'], errors='coerce')
df1['Date'] = df1['Date'].astype(str)

merged = pd.merge(pivoted_source0, df1[['Date', 'NumMosquitos']], on='Date', how='inner')

result = merged[['Date', 'ResultDir', 'NumMosquitos']]

result.to_csv(target_path, index=False)