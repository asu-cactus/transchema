import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

def clean_numeric_column(col):
    if col.dtype == object:
        return pd.to_numeric(col.str.replace(',', '').str.strip(), errors='coerce')
    return col

for df in [df0, df1, df2, df3]:
    df['salary'] = clean_numeric_column(df['salary'])
    df['rate'] = clean_numeric_column(df['rate'])
    df['reviews'] = clean_numeric_column(df['reviews'])
    df['href'] = df['href'].notna().astype(int)

grouped_0 = df0.groupby(['company', 'title', 'location', 'summary', 'org_salary_period'], dropna=False).agg(
    salary_avg=('salary', 'mean'),
    rate_avg=('rate', 'mean'),
    href_count=('href', 'sum'),
    reviews_sum=('reviews', 'sum')
).reset_index()

grouped_1 = df1.groupby(['company', 'title', 'location', 'summary', 'org_salary_period'], dropna=False).agg(
    salary_avg=('salary', 'mean'),
    rate_avg=('rate', 'mean'),
    href_count=('href', 'sum'),
    reviews_sum=('reviews', 'sum')
).reset_index()

grouped_2 = df2.groupby(['company', 'title', 'location', 'summary', 'org_salary_period'], dropna=False).agg(
    salary_avg=('salary', 'mean'),
    rate_avg=('rate', 'mean'),
    href_count=('href', 'sum'),
    reviews_sum=('reviews', 'sum')
).reset_index()

grouped_3 = df3.groupby(['company', 'title', 'location', 'summary', 'org_salary_period'], dropna=False).agg(
    salary_avg=('salary', 'mean'),
    rate_avg=('rate', 'mean'),
    href_count=('href', 'sum'),
    reviews_sum=('reviews', 'sum')
).reset_index()

union_df = pd.concat([grouped_0, grouped_1, grouped_2, grouped_3], ignore_index=True)

final_grouped = union_df.groupby(['company', 'title', 'location', 'summary', 'org_salary_period'], dropna=False).agg(
    salary=('salary_avg', 'sum'),
    rate=('rate_avg', 'sum'),
    href=('href_count', 'sum'),
    reviews=('reviews_sum', 'sum')
).reset_index()

# Convert columns to integer where target schema expects integer
final_grouped['title'] = final_grouped['title'].astype('category').cat.codes + 1
final_grouped['location'] = final_grouped['location'].astype('category').cat.codes + 1
final_grouped['summary'] = final_grouped['summary'].astype('category').cat.codes + 1
final_grouped['org_salary_period'] = final_grouped['org_salary_period'].astype('category').cat.codes + 1

final_grouped['salary'] = final_grouped['salary'].round().astype('Int64')
final_grouped['rate'] = final_grouped['rate'].round().astype('Int64')
final_grouped['href'] = final_grouped['href'].astype('Int64')
final_grouped['reviews'] = final_grouped['reviews'].round().astype('Int64')

final_grouped = final_grouped[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

final_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)