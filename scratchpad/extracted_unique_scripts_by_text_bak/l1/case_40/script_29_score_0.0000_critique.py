import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df = df[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']]

df['ORDERNUMBER'] = pd.to_numeric(df['ORDERNUMBER'], errors='coerce').astype('Int64')
df['QUANTITYORDERED'] = pd.to_numeric(df['QUANTITYORDERED'], errors='coerce').astype('Int64')
df['CUSTOMERNAME'] = df['CUSTOMERNAME'].astype(str)

# Drop rows with NaN in grouping or aggregation columns to avoid errors in groupby
df = df.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED'])

# Group by CUSTOMERNAME and ORDERNUMBER, sum QUANTITYORDERED
df = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False).agg({'QUANTITYORDERED': 'sum'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)