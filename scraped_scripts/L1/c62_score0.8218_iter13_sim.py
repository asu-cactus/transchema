import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)

unpivot = df0.melt(id_vars=['Text Date', 'Value Date', 'Zip Code'], value_vars=['Water Use', 'Power Use'], 
                   var_name='Usage Type', value_name='Usage Value')

pivot = unpivot.pivot_table(index='Text Date', columns='Usage Type', values='Usage Value', aggfunc='first').reset_index()

pivot.rename(columns={'Text Date': 'Month'}, inplace=True)

pivot['Water Use'] = pivot['Water Use'].astype(float)
pivot['Power Use'] = pivot['Power Use'].astype(int)
pivot['Month'] = pivot['Month'].astype(str)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)