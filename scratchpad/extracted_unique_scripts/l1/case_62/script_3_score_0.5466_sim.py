import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)

df = df0.melt(id_vars=['Text Date', 'Value Date', 'Zip Code'], value_vars=['Water Use', 'Power Use'], var_name='Usage Type', value_name='Usage Value')

df['Month'] = df['Text Date']
df = df.drop(columns=['Text Date', 'Value Date', 'Zip Code'])

df_wu = df[df['Usage Type'] == 'Water Use'].copy()
df_pu = df[df['Usage Type'] == 'Power Use'].copy()

df_wu = df_wu.rename(columns={'Usage Value': 'Water Use'}).drop(columns=['Usage Type'])
df_pu = df_pu.rename(columns={'Usage Value': 'Power Use'}).drop(columns=['Usage Type'])

df_final = pd.merge(df_wu, df_pu, on='Month')

df_final['Water Use'] = df_final['Water Use'].astype(float)
df_final['Power Use'] = df_final['Power Use'].astype(int)

df_final = df_final[['Month', 'Water Use', 'Power Use']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)