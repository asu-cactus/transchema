import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['salary'] = pd.to_numeric(df_all['salary'], errors='coerce')
df_all['rate'] = pd.to_numeric(df_all['rate'], errors='coerce')
df_all['reviews'] = pd.to_numeric(df_all['reviews'].str.replace(',', ''), errors='coerce')

group_cols = ['company', 'title', 'location', 'summary', 'org_salary_period']
agg_df = df_all.groupby(group_cols).agg(
    salary_min=('salary', 'min'),
    salary_max=('salary', 'max'),
    href_count=('href', 'count'),
    rate_sum=('rate', 'sum'),
    reviews_sum=('reviews', 'sum')
).reset_index()

# The target schema is:
# ['company': string, 'title': integer, 'location': integer, 'summary': integer, 'salary': integer, 'href': integer, 'rate': integer, 'reviews': integer, 'org_salary_period': integer]
# From the partial plan, salary is aggregated min and max, href is count.
# The target examples show salary as 1, href as 1, rate as 1, reviews as 1, title/location/summary/org_salary_period as integer 1.
# We must convert the string columns title, location, summary, org_salary_period to integer codes.
# For salary, we can take the min and max and combine them by taking the min (or max) or average. The partial plan uses min and max, but target schema has one salary column.
# We'll take the min salary as salary.
# For href, use the count.
# For rate and reviews, sum or mean? The target examples show 1 for all, so we can aggregate by sum or mean. We'll take sum.
# Convert categorical columns to integer codes.

agg_df['salary'] = agg_df['salary_min'].fillna(0).astype(int)
agg_df['href'] = agg_df['href_count'].astype(int)

for col in ['title', 'location', 'summary', 'org_salary_period']:
    agg_df[col] = agg_df[col].astype('category').cat.codes

agg_df['rate'] = agg_df['rate_sum'].fillna(0).astype(int)
agg_df['reviews'] = agg_df['reviews_sum'].fillna(0).astype(int)

result = agg_df[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)