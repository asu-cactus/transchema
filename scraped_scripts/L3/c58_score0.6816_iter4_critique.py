import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_58/training_1.csv", index_col=0)

# Join on Mouse ID (inner join)
df_merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Pivot: index=Timepoint, columns=Drug, values=mean Tumor Volume
pivot = df_merged.pivot_table(index="Timepoint", columns="Drug", values="Tumor Volume (mm3)", aggfunc="mean")

# Reset index to make Timepoint a column
pivot = pivot.reset_index()

# Target columns
expected_cols = ['Timepoint', 'Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol',
                 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']

# Add missing drug columns with NaN
for col in expected_cols[1:]:
    if col not in pivot.columns:
        pivot[col] = pd.NA

# Add the constant row for Timepoint=0 with all drug columns = 45.0
if 0 not in pivot['Timepoint'].values:
    const_row = {'Timepoint': 0}
    for col in expected_cols[1:]:
        const_row[col] = 45.0
    pivot = pd.concat([pd.DataFrame([const_row]), pivot], ignore_index=True)

# Ensure columns order
pivot = pivot[expected_cols]

# Sort by Timepoint ascending
pivot = pivot.sort_values('Timepoint').reset_index(drop=True)

# Write output
pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_58/target_multisource_mcts.csv", index=False)