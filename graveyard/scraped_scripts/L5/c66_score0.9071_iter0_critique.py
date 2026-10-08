import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_66/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_5.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert columns to correct types
df['S/N'] = df['S/N'].astype(str)
df['Building/Project Name'] = df['Building/Project Name'].astype(str)
df['Street Name'] = df['Street Name'].astype(str)
df['Postal District'] = pd.to_numeric(df['Postal District'], errors='coerce')
df['Type'] = df['Type'].astype(str)
df['No. of Bedroom(for Non-Landed Only)'] = df['No. of Bedroom(for Non-Landed Only)'].astype(str)
df['Monthly Gross Rent($)'] = pd.to_numeric(df['Monthly Gross Rent($)'], errors='coerce')
df['Floor Area (sq ft)'] = df['Floor Area (sq ft)'].astype(str)
df['Lease Commencement Date'] = df['Lease Commencement Date'].astype(str)

# Group by 'S/N' and aggregate other columns
agg_dict = {
    'Building/Project Name': 'first',
    'Street Name': 'first',
    'Postal District': 'mean',
    'Type': 'first',
    'No. of Bedroom(for Non-Landed Only)': 'first',
    'Monthly Gross Rent($)': 'mean',
    'Floor Area (sq ft)': 'first',
    'Lease Commencement Date': 'first'
}

df = df.groupby('S/N', as_index=False).agg(agg_dict)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_66/target_multisource_mcts.csv", index=False)