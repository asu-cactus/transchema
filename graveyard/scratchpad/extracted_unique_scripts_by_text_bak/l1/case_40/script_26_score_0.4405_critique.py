import pandas as pd

# List all source files
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_9.csv",
]

dfs = []
for file in source_files:
    df = pd.read_csv(file, index_col=0)
    # Select only needed columns
    df = df[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']].copy()
    # Convert types
    df['ORDERNUMBER'] = pd.to_numeric(df['ORDERNUMBER'], errors='coerce').astype('Int64')
    df['QUANTITYORDERED'] = pd.to_numeric(df['QUANTITYORDERED'], errors='coerce').astype('Int64')
    df['CUSTOMERNAME'] = df['CUSTOMERNAME'].astype(str)
    dfs.append(df)

# Union all source tables by concatenation
df_all = pd.concat(dfs, ignore_index=True)

# Remove rows with NaN in key columns (CUSTOMERNAME or ORDERNUMBER)
df_all = df_all.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])

# Group by CUSTOMERNAME and ORDERNUMBER, sum QUANTITYORDERED
df_grouped = df_all.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False).agg({'QUANTITYORDERED': 'sum'})

# Convert ORDERNUMBER and QUANTITYORDERED to integer dtype (nullable Int64)
df_grouped['ORDERNUMBER'] = df_grouped['ORDERNUMBER'].astype('Int64')
df_grouped['QUANTITYORDERED'] = df_grouped['QUANTITYORDERED'].astype('Int64')

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)