import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_50/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_50/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_50/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df1_union = pd.concat([df1, df1], ignore_index=True)

df_joined = pd.merge(df1_union, df0[['ID', 'sex']], on='ID', how='inner')

grouped = df_joined.groupby('sex').agg({'G1':'mean', 'G2':'mean', 'G3':'mean'}).reset_index()

grouped.to_csv(output_path, index=False)