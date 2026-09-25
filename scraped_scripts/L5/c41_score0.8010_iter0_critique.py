import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_4.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# GROUP BY 'Winner' and aggregate count distinct for other columns
result = df.groupby('Winner').agg(
    Year=('Year', pd.Series.nunique),
    Category=('Category', pd.Series.nunique),
    Nominee=('Nominee', pd.Series.nunique),
    Movie=('Movie', pd.Series.nunique)
).reset_index()

# Ensure integer type for aggregated columns
result['Year'] = result['Year'].astype(int)
result['Category'] = result['Category'].astype(int)
result['Nominee'] = result['Nominee'].astype(int)
result['Movie'] = result['Movie'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_41/target_multisource_mcts.csv", index=False)