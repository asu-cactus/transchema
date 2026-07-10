import pandas as pd
import numpy as np

def safe_to_numeric(series):
    return pd.to_numeric(series.str.replace(',', '').replace('', np.nan), errors='coerce')

def main():
    src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
    src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
    src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
    src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

    # Concatenate all sources
    df = pd.concat([src0, src1, src2, src3], ignore_index=True)

    # Clean and convert columns to appropriate types
    df['salary'] = safe_to_numeric(df['salary'].astype(str))
    df['rate'] = safe_to_numeric(df['rate'].astype(str))
    df['reviews'] = safe_to_numeric(df['reviews'].astype(str))
    # 'href' is a URL string, SUM is requested in plan, so convert to count of non-null as proxy for SUM(href)
    # Because summing URLs is not meaningful, we interpret SUM(href) as count of href occurrences
    # But the plan says SUM(Source4_42_0.href), so we treat href as count of non-null occurrences per group
    # We'll sum 1 for each non-null href
    df['href_count'] = df['href'].notna().astype(int)

    # Group by the specified columns
    grouped = df.groupby(['location', 'title', 'company', 'summary', 'org_salary_period'], dropna=False).agg(
        salary_count = ('salary', 'count'),
        salary_avg = ('salary', 'mean'),
        rate_avg = ('rate', 'mean'),
        href_sum = ('href_count', 'sum'),
        reviews_avg = ('reviews', 'mean')
    ).reset_index()

    # According to target schema:
    # ['location': string, 'title': integer, 'company': integer, 'summary': integer, 'salary': integer, 'href': integer, 'rate': integer, 'reviews': integer, 'org_salary_period': integer]
    # We need to convert title, company, summary, org_salary_period to integer
    # The source columns title, company, summary, org_salary_period are strings, so we encode them as categorical codes
    for col in ['title', 'company', 'summary', 'org_salary_period']:
        grouped[col] = grouped[col].astype('category').cat.codes

    # Convert location to string (already string)
    grouped['location'] = grouped['location'].astype(str)

    # Convert aggregated columns to integer as per target schema
    grouped['salary'] = grouped['salary_avg'].round().fillna(0).astype(int)
    grouped['href'] = grouped['href_sum'].fillna(0).astype(int)
    grouped['rate'] = grouped['rate_avg'].round().fillna(0).astype(int)
    grouped['reviews'] = grouped['reviews_avg'].round().fillna(0).astype(int)

    # Drop intermediate aggregation columns
    grouped = grouped.drop(columns=['salary_count', 'salary_avg', 'rate_avg', 'href_sum', 'reviews_avg'])

    # Reorder columns to match target schema
    grouped = grouped[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

    grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)

if __name__ == "__main__":
    main()