import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_15/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_5.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['State Name'] = df['State Name'].astype(str)
df['county Name'] = df['county Name'].astype(str)
df['Year'] = df['Year'].astype(int)
df['Month'] = df['Month'].astype(int)
df['State Code'] = df['State Code'].astype(int)
df['County Code'] = df['County Code'].astype(int)
df['Date'] = df['Date'].astype(str)
df['AQI'] = df['AQI'].astype(int)
df['Category'] = df['Category'].astype(str)
df['Defining Parameter'] = df['Defining Parameter'].astype(str)
df['Defining Site'] = df['Defining Site'].astype(str)
df['Number of Sites Reporting'] = df['Number of Sites Reporting'].astype(int)

df = df[['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)