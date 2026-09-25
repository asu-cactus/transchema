import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

df0_grouped = df0.groupby('user_id', as_index=False).first()

df01 = pd.merge(df0_grouped, df1, on='user_id', how='inner')

df_final = pd.merge(df01, df2, on='user_id', how='inner')

df_final = df_final[['user_id', 'year_school', 'floor', 'party', 'libcon', 'fav_music']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)