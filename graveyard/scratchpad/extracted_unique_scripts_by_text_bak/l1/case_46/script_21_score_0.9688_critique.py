import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

grouped = df.groupby('Text Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})

grouped.rename(columns={'Text Date': 'Date'}, inplace=True)

grouped['Water Use'] = grouped['Water Use'].astype(float)
grouped['Power Use'] = grouped['Power Use'].astype(int)
grouped['Date'] = grouped['Date'].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)