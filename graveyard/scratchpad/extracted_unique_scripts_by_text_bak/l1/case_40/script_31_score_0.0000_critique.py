import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

union_df = pd.concat(dfs, ignore_index=True)

# Select relevant columns
df = union_df[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']].copy()

# Convert ORDERNUMBER and QUANTITYORDERED to numeric (integer)
df['ORDERNUMBER'] = pd.to_numeric(df['ORDERNUMBER'], errors='coerce').astype('Int64')
df['QUANTITYORDERED'] = pd.to_numeric(df['QUANTITYORDERED'], errors='coerce').astype('Int64')

# Drop rows with NaN in any of the selected columns
df = df.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED'])

# Group by CUSTOMERNAME and ORDERNUMBER, sum QUANTITYORDERED
result = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False).agg({'QUANTITYORDERED': 'sum'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)