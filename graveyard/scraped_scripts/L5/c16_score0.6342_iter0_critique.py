import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_4.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Map Age Group to integers dynamically (no hardcoding)
# Since target examples have integer codes, we map unique Age Group values to unique integers
age_groups = pd.Series(df_all['Age Group'].unique()).sort_values().reset_index(drop=True)
age_map = {k: v for v, k in enumerate(age_groups)}
df_all['Age Group'] = df_all['Age Group'].map(age_map).fillna(5).astype(int)

# Map Sex to integers dynamically
sexes = pd.Series(df_all['Sex'].unique()).sort_values().reset_index(drop=True)
sex_map = {k: v for v, k in enumerate(sexes)}
df_all['Sex'] = df_all['Sex'].map(sex_map).fillna(5).astype(int)

# Convert count columns to numeric, fill NaN with 0, convert to int
for col in ["Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0).astype(int)

# Group by Age Group and Sex, sum the count columns
grouped = df_all.groupby(['Age Group', 'Sex'], as_index=False).sum()

# Assign index as row number (0-based)
grouped['index'] = range(len(grouped))

# Reorder columns to match target schema
grouped = grouped[['index', 'Age Group', 'Sex', "Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']]

# Write to output CSV
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_16/target_multisource_mcts.csv", index=False)