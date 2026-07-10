import pandas as pd

# File paths
file_paths = [
    "autopipeline-benchmarks/github-pipelines/length4_62/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_62/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_62/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_62/training_3.csv"
]

# Read all source tables with index_col=0
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]

# Standardize column names if needed (some columns differ slightly)
# For example, "ACT Score" vs "The ACT Score" vs "ACT Score" in different sources
# We unify these columns by renaming to target schema names

# Define a mapping for known column name differences to target names
rename_map = {
    "The ACT Score": "ACT Score",
    "Passing Math III": "Passing Math III",
    "Passing NC Math 3": "Passing Math III",
    "EOCMathI_GLP_Black": "EOCMathI_GLP_Black",  # same name, just example
    # Add more mappings if needed based on source differences
}

for i, df in enumerate(dfs):
    # Rename columns according to rename_map if present
    df.rename(columns=rename_map, inplace=True)
    # Some sources have columns missing, add missing columns with NaN to align schemas
    # Get all columns from all dfs combined
all_columns = set()
for df in dfs:
    all_columns.update(df.columns)
all_columns = list(all_columns)

for i, df in enumerate(dfs):
    missing_cols = set(all_columns) - set(df.columns)
    for col in missing_cols:
        df[col] = pd.NA
    # Reorder columns to all_columns
    dfs[i] = df[all_columns]

# UNION all dataframes (concatenate rows)
df_all = pd.concat(dfs, ignore_index=True)

# Columns to group by (leftmost non-float unique columns in target)
group_by_cols = ['student_num', 'lea_avg_student_num', 'st_avg_student_num']

# Columns to aggregate: all except group_by_cols
agg_cols = [col for col in df_all.columns if col not in group_by_cols]

# For aggregation, apply mean for all columns (including float and int)
# The target schema shows first column 'Not Demostrated_TCHR_Standard 1_Pct' as float,
# others as integer, so we keep mean for all, then convert to int except first column.

# Aggregate by mean
df_grouped = df_all.groupby(group_by_cols, dropna=False)[agg_cols].mean().reset_index()

# Reorder columns to match target schema order:
# Target schema starts with 'Not Demostrated_TCHR_Standard 1_Pct' then group_by_cols then others
# So we reorder columns accordingly

# Check if 'Not Demostrated_TCHR_Standard 1_Pct' is in columns
if 'Not Demostrated_TCHR_Standard 1_Pct' in df_grouped.columns:
    cols_order = ['Not Demostrated_TCHR_Standard 1_Pct'] + group_by_cols + [c for c in df_grouped.columns if c not in ['Not Demostrated_TCHR_Standard 1_Pct'] + group_by_cols]
else:
    # If missing, just group_by_cols + others
    cols_order = group_by_cols + [c for c in df_grouped.columns if c not in group_by_cols]

df_grouped = df_grouped[cols_order]

# Convert all columns except 'Not Demostrated_TCHR_Standard 1_Pct' to integer (rounding)
for col in df_grouped.columns:
    if col != 'Not Demostrated_TCHR_Standard 1_Pct':
        df_grouped[col] = df_grouped[col].round().astype('Int64')

# Write output to CSV
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_62/target_multisource_mcts.csv", index=False)