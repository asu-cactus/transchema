import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

df = pd.merge(df0, df1, left_on="right_index", right_index=True, suffixes=('_0', '_1'))

result = pd.DataFrame()
result['0_x'] = [df['0_0'].mean()]
result['0_y'] = [df['0_1'].mean()]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)