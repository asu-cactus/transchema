import pandas as pd

# Read all source CSVs
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_4.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Group by "Age Group" and "Sex" and sum the numeric columns
group_cols = ["Age Group", "Sex"]
sum_cols = ["Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]

df_grouped = df_all.groupby(group_cols, dropna=False)[sum_cols].sum(min_count=1).reset_index()

# Mapping dictionaries for Age Group and Sex
age_map = {
    "Age 18 to 24": 5,
    "Age 25 to 34": 6,
    "Age 35 to 44": 7,
    "Age 45 to 54": 8,
    "Age 55 to 64": 9,
    "Age 65 to 74": 10,
    "Age 75+": 11,
    "Refused": 12
}

sex_map = {
    "Female": 5,
    "Male": 5,
    "Refused": 5
}

# Map Age Group and Sex to integers
df_grouped["Age Group"] = df_grouped["Age Group"].map(age_map).astype("Int64")
df_grouped["Sex"] = df_grouped["Sex"].map(sex_map).astype("Int64")

# Add index column as integer index
df_grouped = df_grouped.reset_index(drop=True)
df_grouped["index"] = df_grouped.index.astype(int)

# Reorder columns to match target schema
final_cols = ["index", "Age Group", "Sex", "Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]
result = df_grouped[final_cols]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_16/target_multisource_mcts.csv", index=False)