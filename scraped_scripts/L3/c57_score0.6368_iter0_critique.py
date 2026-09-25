import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_57/training_0.csv", index_col=0)  # Source3_57_0
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_57/training_1.csv", index_col=0)  # Source3_57_1

# Join on Mouse ID
df_joined = pd.merge(df1, df0, on="Mouse ID")

# Group by Timepoint and Drug, count Mouse ID (number of mice per drug per timepoint)
grouped = df_joined.groupby(['Timepoint', 'Drug'], as_index=False).agg({'Mouse ID': 'count'})

# Pivot to get drugs as columns, values are counts
pivot = grouped.pivot(index='Timepoint', columns='Drug', values='Mouse ID')

# Reset index to make Timepoint a column
pivot = pivot.reset_index()

# Target columns
expected_cols = ['Timepoint', 'Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']

# Add missing drug columns with 0 counts
for col in expected_cols[1:]:
    if col not in pivot.columns:
        pivot[col] = 0

# Reorder columns to match target schema
pivot = pivot[expected_cols]

# Convert Timepoint to int
pivot['Timepoint'] = pivot['Timepoint'].astype(int)

# Convert drug columns to correct types according to target schema
# Capomulin: int, Ceftamin: float, Infubinol: int, Ketapril: float, Naftisol: float, Placebo: int, Propriva: int, Ramicane: float, Stelasyn: float, Zoniferol: int
int_cols = ['Capomulin', 'Infubinol', 'Placebo', 'Propriva', 'Zoniferol']
float_cols = ['Ceftamin', 'Ketapril', 'Naftisol', 'Ramicane', 'Stelasyn']

pivot[int_cols] = pivot[int_cols].astype('Int64')
pivot[float_cols] = pivot[float_cols].astype(float)

# Write output
pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_57/target_multisource_mcts.csv", index=False)