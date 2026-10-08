import pandas as pd

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
    grouped = df.groupby([
        'State Name', 'county Name', 'State Code', 'County Code',
        'Category', 'Defining Parameter', 'Defining Site',
        'Year', 'Month', 'Date'
    ], dropna=False).agg({
        'AQI': 'mean',
        'Number of Sites Reporting': 'sum'
    }).reset_index()
    grouped['AQI'] = grouped['AQI'].round().astype('Int64')
    grouped['Number of Sites Reporting'] = grouped['Number of Sites Reporting'].astype('Int64')
    agg_dfs.append(grouped)

result = pd.concat(agg_dfs, ignore_index=True)

result = result[[
    'State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code',
    'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting'
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)