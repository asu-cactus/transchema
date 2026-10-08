import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['Text Date'], value_vars=['Water Use', 'Power Use'], var_name='Measure', value_name='Value')

df_pivot = df_unpivot.pivot_table(index='Text Date', columns='Measure', values='Value', aggfunc='first').reset_index()

df_pivot.rename(columns={'Text Date': 'Date'}, inplace=True)

df_pivot['Water Use'] = df_pivot['Water Use'].astype(float)
df_pivot['Power Use'] = df_pivot['Power Use'].astype(int)
df_pivot['Date'] = df_pivot['Date'].astype(str)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)