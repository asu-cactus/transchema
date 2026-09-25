import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_17/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_5.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert columns to correct types as per target schema
df['S/N'] = df['S/N'].astype(int)
df['Postal District'] = df['Postal District'].astype(int)
df['Monthly Gross Rent($)'] = df['Monthly Gross Rent($)'].astype(int)

# Other columns as string
df['Building/Project Name'] = df['Building/Project Name'].astype(str)
df['Street Name'] = df['Street Name'].astype(str)
df['Type'] = df['Type'].astype(str)
df['No. of Bedroom(for Non-Landed Only)'] = df['No. of Bedroom(for Non-Landed Only)'].astype(str)
df['Floor Area (sq ft)'] = df['Floor Area (sq ft)'].astype(str)
df['Lease Commencement Date'] = df['Lease Commencement Date'].astype(str)

# Group by 'S/N' and aggregate other columns by first value to ensure uniqueness
df_final = df.groupby('S/N', as_index=False).agg({
    'Building/Project Name': 'first',
    'Street Name': 'first',
    'Postal District': 'first',
    'Type': 'first',
    'No. of Bedroom(for Non-Landed Only)': 'first',
    'Monthly Gross Rent($)': 'first',
    'Floor Area (sq ft)': 'first',
    'Lease Commencement Date': 'first'
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_17/target_multisource_mcts.csv", index=False)