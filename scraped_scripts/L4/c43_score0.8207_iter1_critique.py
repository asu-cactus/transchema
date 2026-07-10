import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean 'reviews' column: remove commas and convert to numeric
df['reviews'] = pd.to_numeric(df['reviews'].astype(str).str.replace(',', ''), errors='coerce')

# Convert 'salary' and 'rate' to numeric (some may be strings)
df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')

# Group by 'company' (string, leftmost unique column)
grouped = df.groupby('company', dropna=False)

# Aggregate numeric columns by mean
agg_df = grouped.agg({
    'salary': 'mean',
    'rate': 'mean',
    'reviews': 'mean',
    'title': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
    'location': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
    'summary': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
    'href': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
    'org_salary_period': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
})

# After aggregation, encode categorical string columns as integer codes
for col in ['title', 'location', 'summary', 'href', 'org_salary_period']:
    agg_df[col] = agg_df[col].astype('category').cat.codes

# Convert numeric columns to int (round first)
agg_df['salary'] = agg_df['salary'].round().astype('Int64')
agg_df['rate'] = agg_df['rate'].round().astype('Int64')
agg_df['reviews'] = agg_df['reviews'].round().astype('Int64')

# Reset index to have 'company' as a column
agg_df = agg_df.reset_index()

# Reorder columns to match target schema
agg_df = agg_df[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write to output CSV
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)