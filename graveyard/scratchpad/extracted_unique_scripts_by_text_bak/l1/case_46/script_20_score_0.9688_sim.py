import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

unpivoted = df.melt(id_vars=['Text Date'], value_vars=['Water Use', 'Power Use'], var_name='Measure', value_name='Value')

grouped = unpivoted.groupby(['Text Date', 'Measure'], as_index=False)['Value'].sum()

pivoted = grouped.pivot(index='Text Date', columns='Measure', values='Value').reset_index()

pivoted.rename(columns={'Text Date': 'Date'}, inplace=True)

pivoted['Water Use'] = pivoted['Water Use'].astype(float)
pivoted['Power Use'] = pivoted['Power Use'].astype(int)
pivoted['Date'] = pivoted['Date'].astype(str)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)