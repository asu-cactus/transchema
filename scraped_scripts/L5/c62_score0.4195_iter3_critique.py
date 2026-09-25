import pandas as pd

# Read all source CSVs
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_4.csv", index_col=0)

# Combine all source tables by union (concatenate)
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Convert 'Age Group' from string like 'Age 18 to 24' to integer 18 (start age)
def extract_start_age(age_group_str):
    if pd.isna(age_group_str):
        return pd.NA
    parts = age_group_str.split()
    for part in parts:
        if part.isdigit():
            return int(part)
    return pd.NA

df_all['Age Group'] = df_all['Age Group'].apply(extract_start_age).astype('Int64')

# Group by 'Sex' and 'Age Group' and sum the count columns
group_cols = ['Sex', 'Age Group']
agg_cols = ["Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]

result = df_all.groupby(group_cols, dropna=False)[agg_cols].sum(min_count=1).reset_index()

# Convert aggregation columns to integer type with nullable Int64 dtype
for col in agg_cols:
    result[col] = result[col].astype('Int64')

# Reorder columns to match target schema exactly
result = result[['Sex', 'Age Group', "Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_62/target_multisource_mcts.csv", index=False)