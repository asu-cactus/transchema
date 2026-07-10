import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Clean data by removing rows where 'age_grp' or 'Statistics' are invalid header-like or total rows
# We do not hardcode values but remove rows where 'age_grp' or 'Statistics' are NaN or equal to 'Year' or 'Total for selection' or similar
# Since 'age_grp' and 'Statistics' are string columns, remove rows where 'age_grp' or 'Statistics' are null or contain header-like values

# Convert to string to safely check values
df['age_grp'] = df['age_grp'].astype(str).str.strip()
df['Statistics'] = df['Statistics'].astype(str).str.strip()

# Filter out rows where 'age_grp' or 'Statistics' are header-like or invalid
invalid_age_grp = ['Year', 'Total for selection', 'Unnamed: 1', 'nan', 'NaN', 'None', '']
invalid_statistics = ['Year', 'Total for selection', 'Unnamed: 1', 'nan', 'NaN', 'None', '']

df = df[~df['age_grp'].isin(invalid_age_grp)]
df = df[~df['Statistics'].isin(invalid_statistics)]

# Reset index after filtering
df = df.reset_index(drop=True)

# Keep columns in target schema order
df = df[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)