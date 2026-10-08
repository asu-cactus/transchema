import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all = df_all[df_all['company'].notna()]

agg_dict = {
    'title': pd.Series.nunique,
    'location': pd.Series.nunique,
    'summary': pd.Series.nunique,
    'salary': pd.Series.nunique,
    'href': pd.Series.nunique,
    'rate': pd.Series.nunique,
    'reviews': pd.Series.nunique,
    'org_salary_period': pd.Series.nunique
}

df_grouped = df_all.groupby('company', dropna=False).agg(agg_dict).reset_index()

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)