import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_2.csv", index_col=0)

df_unpivot = source1.melt(id_vars=['movie_id'], value_vars=['rating'], var_name='variable', value_name='0')
result = df_unpivot[['movie_id', '0']].copy()
result['0'] = result['0'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_93/target_multisource_mcts.csv", index=False)