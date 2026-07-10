import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_17/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_5.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert types as per target schema
df['S/N'] = df['S/N'].astype(int)
df['Postal District'] = df['Postal District'].astype(int)
df['Monthly Gross Rent($)'] = df['Monthly Gross Rent($)'].astype(int)

# Select columns in target schema order
df = df[['S/N', 'Building/Project Name', 'Street Name', 'Postal District', 'Type',
         'No. of Bedroom(for Non-Landed Only)', 'Monthly Gross Rent($)', 'Floor Area (sq ft)', 'Lease Commencement Date']]

# Group by leftmost columns that form the key
group_cols = ['S/N', 'Building/Project Name', 'Street Name', 'Postal District', 'Type', 'No. of Bedroom(for Non-Landed Only)']

# Aggregate other columns
agg_dict = {
    'Monthly Gross Rent($)': 'max',
    'Floor Area (sq ft)': 'first',
    'Lease Commencement Date': 'first'
}

df = df.groupby(group_cols, as_index=False).agg(agg_dict)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_17/target_multisource_mcts.csv", index=False)