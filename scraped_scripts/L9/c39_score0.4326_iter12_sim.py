import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_9.csv", index_col=0)
df10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_10.csv", index_col=0)

df_agg = pd.DataFrame()
df_agg['0'] = df0['0']

df_agg['sum_1'] = df1['0']
df_agg['sum_2'] = df2['0']
df_agg['sum_4'] = df4['0']
df_agg['sum_5'] = df5['0']
df_agg['sum_6'] = df6['0']
df_agg['sum_8'] = df8['0']
df_agg['sum_9'] = df9['0']
df_agg['sum_10'] = df10['0']

df_agg['0'] = df_agg['0'] + df_agg['sum_1'] + df_agg['sum_2'] + df_agg['sum_4'] + df_agg['sum_5'] + df_agg['sum_6'] + df_agg['sum_8'] + df_agg['sum_9'] + df_agg['sum_10']

df_agg = df_agg[['0']]

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length9_39/target_multisource_mcts.csv")