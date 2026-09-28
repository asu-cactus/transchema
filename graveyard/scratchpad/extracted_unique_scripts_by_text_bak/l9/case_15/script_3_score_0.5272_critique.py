import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_15/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_5.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes
df = df.astype({
    'Year': 'int',
    'Month': 'int',
    'State Code': 'int',
    'County Code': 'int',
    'AQI': 'int',
    'Number of Sites Reporting': 'int',
    'Date': 'string',
    'State Name': 'string',
    'county Name': 'string',
    'Category': 'string',
    'Defining Parameter': 'string',
    'Defining Site': 'string',
})

# Define group by columns (key columns)
group_by_cols = ['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date', 'Category', 'Defining Parameter', 'Defining Site']

# Aggregate AQI by max, Number of Sites Reporting by sum
agg_dict = {
    'AQI': 'max',
    'Number of Sites Reporting': 'sum'
}

df_agg = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
df_agg = df_agg[['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']]

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)