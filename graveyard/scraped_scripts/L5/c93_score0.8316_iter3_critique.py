import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_4.csv", index_col=0)

# For each source, group by Category and count rows (count Year as proxy)
g0 = df0.groupby('Category').agg(Year=('Year', 'count')).reset_index()
g1 = df1.groupby('Category').agg(Nominee=('Year', 'count')).reset_index()
g2 = df2.groupby('Category').agg(Movie=('Year', 'count')).reset_index()
g3 = df3.groupby('Category').agg(Winner=('Year', 'count')).reset_index()
g4 = df4.groupby('Category').agg(Winner_4=('Year', 'count')).reset_index()

# Join all grouped dataframes on Category
df_join = g0.merge(g1, on='Category', how='outer') \
            .merge(g2, on='Category', how='outer') \
            .merge(g3, on='Category', how='outer') \
            .merge(g4, on='Category', how='outer')

# The target schema has only one Winner column, presumably sum counts from df3 and df4
# Sum Winner counts from df3 and df4 (both are counts of rows from different sources)
df_join['Winner'] = df_join['Winner'].fillna(0).astype(int) + df_join['Winner_4'].fillna(0).astype(int)

# Drop the extra Winner_4 column
df_join = df_join.drop(columns=['Winner_4'])

# Fill NaN counts with 0 and convert to int
for col in ['Year', 'Nominee', 'Movie', 'Winner']:
    df_join[col] = df_join[col].fillna(0).astype(int)

# Reorder columns to match target schema
df_join = df_join[['Category', 'Year', 'Nominee', 'Movie', 'Winner']]

# Write output
df_join.to_csv("autopipeline-benchmarks/github-pipelines/length5_93/target_multisource_mcts.csv", index=False)