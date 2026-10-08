import pandas as pd
import re

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_62/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Concatenate all source tables (UNION)
df = pd.concat(dfs, ignore_index=True)

# Convert 'Age Group' to integer by extracting digits (to match target schema)
# This is done before aggregation to keep consistent types, though not used in groupby
df['Age Group'] = df['Age Group'].astype(str).str.extract(r'(\d+)').astype(int)

# Group by 'Sex' only, aggregate sums of all other columns except 'Age Group' and 'Sex'
agg_cols = ["Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']

df_grouped = df.groupby('Sex', dropna=False, as_index=False)[agg_cols].sum()

# For 'Age Group' in target schema, the examples show integer values but only 3 rows,
# so we can aggregate 'Age Group' by sum or count? The target examples show 27, 27, 3 for 'Age Group',
# which looks like counts or sums. Since 'Age Group' is not numeric in source (it's categorical),
# but converted to int, summing it doesn't make sense.
# Instead, we can count the number of rows per Sex for 'Age Group' column to match target counts.

# Count of rows per Sex (to fill 'Age Group' column)
age_group_counts = df.groupby('Sex', dropna=False).size().reset_index(name='Age Group')

# Merge counts into df_grouped
df_grouped = df_grouped.merge(age_group_counts, on='Sex', how='left')

# Reorder columns to match target schema: ['Sex', 'Age Group', "Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']
df_grouped = df_grouped[['Sex', 'Age Group', "Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']]

# Convert all numeric columns to int (target schema expects integer)
for col in df_grouped.columns:
    if col != 'Sex':
        df_grouped[col] = df_grouped[col].fillna(0).astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_62/target_multisource_mcts.csv", index=False)