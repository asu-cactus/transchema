import pandas as pd

# File paths
files = [
    "autopipeline-benchmarks/github-pipelines/length5_66/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length5_66/training_5.csv",
]

# Read all source tables with index_col=0 to ignore the first numerical index column
dfs = [pd.read_csv(f, index_col=0) for f in files]

# Concatenate all source tables (UNION)
df = pd.concat(dfs, ignore_index=True)

# Convert 'S/N' to string to match target schema
df['S/N'] = df['S/N'].astype(str)

# Convert 'No. of Bedroom(for Non-Landed Only)' to string to match target schema
df['No. of Bedroom(for Non-Landed Only)'] = df['No. of Bedroom(for Non-Landed Only)'].astype(str)

# Convert 'Postal District' to float (already float in sources, but ensure)
df['Postal District'] = pd.to_numeric(df['Postal District'], errors='coerce')

# Convert 'Monthly Gross Rent($)' to float (already float, but ensure)
df['Monthly Gross Rent($)'] = pd.to_numeric(df['Monthly Gross Rent($)'], errors='coerce')

# The rest columns are strings, ensure their type
df['Building/Project Name'] = df['Building/Project Name'].astype(str)
df['Street Name'] = df['Street Name'].astype(str)
df['Type'] = df['Type'].astype(str)
df['Floor Area (sq ft)'] = df['Floor Area (sq ft)'].astype(str)
df['Lease Commencement Date'] = df['Lease Commencement Date'].astype(str)

# Group by 'S/N' to ensure uniqueness, aggregate 'Monthly Gross Rent($)' by mean
# For other columns, take first non-null value (assuming no conflicts)
agg_dict = {
    'Building/Project Name': 'first',
    'Street Name': 'first',
    'Postal District': 'first',
    'Type': 'first',
    'No. of Bedroom(for Non-Landed Only)': 'first',
    'Monthly Gross Rent($)': 'mean',
    'Floor Area (sq ft)': 'first',
    'Lease Commencement Date': 'first',
}

df_final = df.groupby('S/N', as_index=False).agg(agg_dict)

# Write to CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_66/target_multisource_mcts.csv", index=False)