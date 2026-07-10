import pandas as pd
import numpy as np

def convert_to_int_series(s):
    # Convert series to integer codes for categorical/string columns
    return s.astype('category').cat.codes + 1

def main():
    paths = [
        "autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv",
        "autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv",
        "autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv",
        "autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv"
    ]
    dfs = [pd.read_csv(p, index_col=0) for p in paths]
    df_all = pd.concat(dfs, ignore_index=True)

    # Normalize 'reviews' column: remove commas and convert to float
    df_all['reviews'] = df_all['reviews'].astype(str).str.replace(',', '', regex=False)
    df_all['reviews'] = pd.to_numeric(df_all['reviews'], errors='coerce')

    # Normalize 'org_salary_period' column: convert to categorical codes
    df_all['org_salary_period'] = df_all['org_salary_period'].astype(str)
    df_all['org_salary_period'] = convert_to_int_series(df_all['org_salary_period'])

    # Convert string columns to integer codes for aggregation
    df_all['title_code'] = convert_to_int_series(df_all['title'])
    df_all['location_code'] = convert_to_int_series(df_all['location'])
    df_all['summary_code'] = convert_to_int_series(df_all['summary'])
    df_all['href_code'] = convert_to_int_series(df_all['href'])

    # Group by company and aggregate
    grouped = df_all.groupby('company').agg(
        title=('title_code', 'count'),
        location=('location_code', 'mean'),
        summary=('summary_code', 'mean'),
        salary=('salary', 'mean'),
        href=('href_code', 'mean'),
        rate=('rate', 'mean'),
        reviews=('reviews', 'mean'),
        org_salary_period=('org_salary_period', 'mean')
    ).reset_index()

    # Round and convert to int as target schema expects integers for all except company
    grouped['title'] = grouped['title'].astype(int)
    grouped['location'] = grouped['location'].round().astype(int)
    grouped['summary'] = grouped['summary'].round().astype(int)
    grouped['salary'] = grouped['salary'].round().astype(int)
    grouped['href'] = grouped['href'].round().astype(int)
    grouped['rate'] = grouped['rate'].round().astype(int)
    grouped['reviews'] = grouped['reviews'].round().astype(int)
    grouped['org_salary_period'] = grouped['org_salary_period'].round().astype(int)

    # Rename columns to match target schema exactly
    grouped = grouped.rename(columns={'title': 'title',
                                      'location': 'location',
                                      'summary': 'summary',
                                      'salary': 'salary',
                                      'href': 'href',
                                      'rate': 'rate',
                                      'reviews': 'reviews',
                                      'org_salary_period': 'org_salary_period'})

    grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)

if __name__ == "__main__":
    main()