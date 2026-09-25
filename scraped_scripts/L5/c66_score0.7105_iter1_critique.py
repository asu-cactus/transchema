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

# Convert columns to appropriate types
df['S/N'] = df['S/N'].astype('string')
df['Building/Project Name'] = df['Building/Project Name'].astype('string')
df['Street Name'] = df['Street Name'].astype('string')
df['Type'] = df['Type'].astype('string')
df['No. of Bedroom(for Non-Landed Only)'] = df['No. of Bedroom(for Non-Landed Only)'].astype('string')
df['Floor Area (sq ft)'] = df['Floor Area (sq ft)'].astype('string')
df['Lease Commencement Date'] = df['Lease Commencement Date'].astype('string')

df['Postal District'] = pd.to_numeric(df['Postal District'], errors='coerce')
df['Monthly Gross Rent($)'] = pd.to_numeric(df['Monthly Gross Rent($)'], errors='coerce')

# Group by key columns and aggregate
agg_dict = {
    'Postal District': 'mean',
    'Monthly Gross Rent($)': 'mean',
    'Type': 'first',
    'No. of Bedroom(for Non-Landed Only)': 'first',
    'Floor Area (sq ft)': 'first',
    'Lease Commencement Date': 'first'
}

df_grouped = df.groupby(['S/N', 'Building/Project Name', 'Street Name'], dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema
df_grouped = df_grouped[['S/N', 'Building/Project Name', 'Street Name', 'Postal District', 'Type',
                         'No. of Bedroom(for Non-Landed Only)', 'Monthly Gross Rent($)', 'Floor Area (sq ft)', 'Lease Commencement Date']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_66/target_multisource_mcts.csv", index=False)