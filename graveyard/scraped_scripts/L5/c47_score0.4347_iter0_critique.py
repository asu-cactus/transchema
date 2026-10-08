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

# Define aggregation functions
agg_dict = {
    'PolityName': lambda x: x.nunique(dropna=True),
    'StartYear': lambda x: x.nunique(dropna=True),
    'StartMonth': lambda x: x.nunique(dropna=True),
    'StartDay': lambda x: x.nunique(dropna=True),
    'EndYear': lambda x: x.nunique(dropna=True),
    'EndMonth': lambda x: x.nunique(dropna=True),
    'EndDay': lambda x: x.nunique(dropna=True),
    'Initiator': lambda x: x.nunique(dropna=True),
    'Deaths': 'sum'
}

grouped = df.groupby(['Outcome', 'WarID'], dropna=False).agg(agg_dict).reset_index()

# Convert all columns to integer type as required by target schema
for col in grouped.columns:
    grouped[col] = pd.to_numeric(grouped[col], errors='coerce').fillna(0).astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)