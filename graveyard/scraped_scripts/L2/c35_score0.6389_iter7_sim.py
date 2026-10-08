import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_35/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_35/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_35/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg_source1 = df1.groupby('Date', as_index=False).agg(
    NumMosquitos_sum=pd.NamedAgg(column='NumMosquitos', aggfunc='sum'),
    NumMosquitos_count=pd.NamedAgg(column='NumMosquitos', aggfunc='count')
)

merged = pd.merge(agg_source1, df0[['Date', 'ResultDir']], on='Date', how='inner')

merged['NumMosquitos'] = merged['NumMosquitos_sum'] / merged['NumMosquitos_count']

result = merged[['Date', 'ResultDir', 'NumMosquitos']]

result.to_csv(target_path, index=False)