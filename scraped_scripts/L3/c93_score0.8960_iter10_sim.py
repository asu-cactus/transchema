import pandas as pd

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_1.csv", index_col=0)
unpivoted = source1.melt(id_vars=['movie_id'], value_vars=['rating'], var_name='variable', value_name='value')
grouped = unpivoted.groupby('movie_id', as_index=False)['value'].sum()
result = grouped.rename(columns={'value': '0'})[['movie_id', '0']]
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_93/target_multisource_mcts.csv", index=False)