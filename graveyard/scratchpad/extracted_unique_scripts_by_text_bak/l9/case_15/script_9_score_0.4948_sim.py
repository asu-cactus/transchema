import pandas as pd
import numpy as np

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_15/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_5.csv"
]

agg_dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    group_cols = ['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']
    agg_df = df.groupby(group_cols, dropna=False, as_index=False)['AQI'].mean()
    agg_df['AQI'] = agg_df['AQI'].round().astype(int)
    agg_dfs.append(agg_df)

result = pd.concat(agg_dfs, ignore_index=True)

result['Year'] = result['Year'].astype(int)
result['Month'] = result['Month'].astype(int)
result['State Code'] = result['State Code'].astype(int)
result['County Code'] = result['County Code'].astype(int)
result['Number of Sites Reporting'] = result['Number of Sites Reporting'].astype(int)
result['Date'] = result['Date'].astype(str)
result['State Name'] = result['State Name'].astype(str)
result['county Name'] = result['county Name'].astype(str)
result['Category'] = result['Category'].astype(str)
result['Defining Parameter'] = result['Defining Parameter'].astype(str)
result['Defining Site'] = result['Defining Site'].astype(str)

result = result[['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)