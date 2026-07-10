import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['title'] = pd.to_numeric(df['title'], errors='coerce').fillna(df['title'])
df['company'] = df['company'].astype(str)

for col in ['location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.extract(r'(\d+\.?\d*)')[0], errors='coerce')

df = df[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)