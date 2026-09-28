import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_47/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

grouped = df.groupby('Outcome', dropna=False).agg({
    'WarID': 'sum',
    'PolityName': 'sum',
    'StartYear': 'sum',
    'StartMonth': 'sum',
    'StartDay': 'sum',
    'EndYear': 'sum',
    'EndMonth': 'sum',
    'EndDay': 'sum',
    'Initiator': lambda x: x.astype(str).str.len().sum() if x.dtype == object else x.sum(),
    'Deaths': 'sum'
}).reset_index()

# Convert all columns to integer type as required by target schema
for col in grouped.columns:
    if col != 'Initiator':
        grouped[col] = pd.to_numeric(grouped[col], errors='coerce').fillna(0).astype(int)
    else:
        # For Initiator, convert string lengths sum to int (already int)
        grouped[col] = grouped[col].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)