import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

df['Date'] = df['Value Date'].str.replace('-', '_')
result = df.groupby('Date', as_index=False).agg({
    'Water Use': 'sum',
    'Power Use': 'sum'
})

result['Water Use'] = result['Water Use'].astype(float)
result['Power Use'] = result['Power Use'].astype(int)

result = result[['Date', 'Water Use', 'Power Use']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)