import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# UNION all sources
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert string columns (except 'company') to categorical codes (integers)
for col in ['title', 'location', 'summary', 'href', 'org_salary_period']:
    df[col] = df[col].astype('category').cat.codes

# Convert numeric columns to numeric types
df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
df['reviews'] = pd.to_numeric(df['reviews'].str.replace(',', ''), errors='coerce')  # remove commas in reviews

# Group by 'company' and aggregate other columns by mean, then convert to int
agg_dict = {
    'title': 'mean',
    'location': 'mean',
    'summary': 'mean',
    'salary': 'mean',
    'href': 'mean',
    'rate': 'mean',
    'reviews': 'mean',
    'org_salary_period': 'mean'
}

df_grouped = df.groupby('company', as_index=False).agg(agg_dict)

# Round aggregated columns to int
for col in ['title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']:
    df_grouped[col] = df_grouped[col].round().astype(int)

# Reorder columns to match target schema
df_grouped = df_grouped[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)