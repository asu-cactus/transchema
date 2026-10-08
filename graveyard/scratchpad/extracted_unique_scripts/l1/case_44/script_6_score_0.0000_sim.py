import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

df_unpivot = df0[['Country / territory of asylum/residence', 'Year', 'Value']]

df_unpivot = df_unpivot.rename(columns={'Value': 'Year'})

df_unpivot['Year'] = pd.to_numeric(df_unpivot['Year'], errors='coerce').fillna(0).astype(int)

df_unpivot = df_unpivot.rename(columns={'Country / territory of asylum/residence': 'Country / territory of asylum/residence'})

df_unpivot = df_unpivot[['Country / territory of asylum/residence', 'Year']]

df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)