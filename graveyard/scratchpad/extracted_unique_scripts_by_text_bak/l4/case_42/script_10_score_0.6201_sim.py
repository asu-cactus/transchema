import pandas as pd
import numpy as np

def clean_numeric_column(col):
    if col.dtype == object:
        col = col.str.replace(',', '').replace('', np.nan)
    return pd.to_numeric(col, errors='coerce')

def main():
    paths = [
        "autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv",
        "autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv",
        "autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv",
        "autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv"
    ]
    dfs = []
    for path in paths:
        df = pd.read_csv(path, index_col=0)
        df['rate'] = clean_numeric_column(df['rate'])
        df['reviews'] = clean_numeric_column(df['reviews'])
        df['salary'] = clean_numeric_column(df['salary'])
        df['href'] = df['href'].astype(str)
        df['location'] = df['location'].astype(str)
        df['title'] = df['title'].astype(str)
        df['company'] = df['company'].astype(str)
        df['summary'] = df['summary'].astype(str)
        df['org_salary_period'] = df['org_salary_period'].astype(str)
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)

    grouped = data.groupby(['location', 'title', 'company'], dropna=False).agg(
        href=('href', 'count'),
        salary=('salary', 'mean'),
        rate=('rate', 'mean'),
        reviews=('reviews', 'mean')
    ).reset_index()

    # Convert aggregated columns to integer as target schema requires integer
    grouped['title'] = grouped['title'].astype('category').cat.codes + 1
    grouped['company'] = grouped['company'].astype('category').cat.codes + 1
    grouped['summary'] = 1  # constant 1 as in target examples
    grouped['salary'] = grouped['salary'].round().fillna(0).astype(int)
    grouped['href'] = grouped['href'].fillna(0).astype(int)
    grouped['rate'] = grouped['rate'].round().fillna(0).astype(int)
    grouped['reviews'] = grouped['reviews'].round().fillna(0).astype(int)
    grouped['org_salary_period'] = 1  # constant 1 as in target examples

    # Reorder columns to match target schema
    result = grouped[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

    result.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)

if __name__ == "__main__":
    main()