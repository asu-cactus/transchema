import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

df0['Value'] = pd.to_numeric(df0['Value'], errors='coerce')

pivoted = df0.pivot_table(index=['Country / territory of asylum/residence', 'Year'], 
                         values='Value', aggfunc='sum').reset_index()

pivoted['Year'] = pivoted['Year'].astype(int)

pivoted = pivoted.rename(columns={'Country / territory of asylum/residence': 'Country / territory of asylum/residence',
                                 'Year': 'Year'})

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)