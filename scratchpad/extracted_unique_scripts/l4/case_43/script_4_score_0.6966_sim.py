import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['reviews'] = df_all['reviews'].astype(str).str.replace(',', '').astype(float)
df_all['rate'] = pd.to_numeric(df_all['rate'], errors='coerce')
df_all['salary'] = pd.to_numeric(df_all['salary'], errors='coerce')

agg = df_all.groupby(['company', 'title', 'location'], dropna=False).agg(
    href=('href', 'count'),
    salary=('salary', 'mean'),
    rate=('rate', 'mean'),
    reviews=('reviews', 'mean')
).reset_index()

# Map string columns to integer codes as target schema expects integers for title, location, summary, org_salary_period
# summary and org_salary_period are not in group_by, so we assign constant 1 as in target examples
agg['title'] = agg['title'].astype('category').cat.codes + 1
agg['location'] = agg['location'].astype('category').cat.codes + 1
agg['summary'] = 1
agg['org_salary_period'] = 1

# company remains string as per target schema
# href, salary, rate, reviews are numeric from aggregation

# Reorder columns to target schema order:
# ['company': string, 'title': integer, 'location': integer, 'summary': integer, 'salary': integer, 'href': integer, 'rate': integer, 'reviews': integer, 'org_salary_period': integer]

# Convert aggregated floats to integers by rounding as target examples show integers
agg['salary'] = agg['salary'].round().astype('Int64')
agg['href'] = agg['href'].astype('Int64')
agg['rate'] = agg['rate'].round().astype('Int64')
agg['reviews'] = agg['reviews'].round().astype('Int64')

agg = agg[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)