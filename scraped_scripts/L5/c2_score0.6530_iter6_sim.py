import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)

join_0 = pd.merge(df4, df0, on="zipcode", suffixes=('_x', '_x_5'))
join_1 = pd.merge(join_0, df2, on="zipcode", suffixes=('', '_y_7'))
join_2 = pd.merge(join_1, df3, on="zipcode", suffixes=('', '_y_8'))

# Rename columns from df4, df0, df2, df3 to match target schema:
# df4: businesses -> businesses_x, counts -> counts_x
# df0: businesses -> businesses_x_5, counts -> counts_x_6
# df2: businesses -> businesses_y, counts -> counts_y
# df3: businesses -> businesses_y_7, counts -> counts_y_8

join_2 = join_2.rename(columns={
    'businesses': 'businesses_x',
    'counts': 'counts_x',
    'businesses_x_5': 'businesses_x_5',
    'counts_x_5': 'counts_x_6',
    'businesses_y_7': 'businesses_y_7',
    'counts_y_7': 'counts_y_8',
    'businesses_y': 'businesses_y',
    'counts_y': 'counts_y'
})

# The suffixes in merge may not have created all columns as expected, so explicitly rename columns from each source:
# After merges, columns from df0 have suffix '_x_5' for businesses and counts
# columns from df2 have suffix '' (no suffix) for businesses and counts, but we renamed them to businesses_y and counts_y
# columns from df3 have suffix '_y_8' for counts, and '_y_7' for businesses

# Actually, to avoid confusion, rename columns explicitly after each merge:

# After first merge (df4 and df0):
join_0 = pd.merge(df4, df0, on="zipcode", suffixes=('_x', '_x_5'))
join_0 = join_0.rename(columns={
    'businesses_x': 'businesses_x',
    'counts_x': 'counts_x',
    'businesses_x_5': 'businesses_x_5',
    'counts_x_5': 'counts_x_6'
})

# After second merge (join_0 and df2):
join_1 = pd.merge(join_0, df2, on="zipcode", suffixes=('', '_y'))
join_1 = join_1.rename(columns={
    'businesses': 'businesses_y',
    'counts': 'counts_y'
})

# After third merge (join_1 and df3):
join_2 = pd.merge(join_1, df3, on="zipcode", suffixes=('', '_y'))
join_2 = join_2.rename(columns={
    'businesses': 'businesses_y_7',
    'counts': 'counts_y_8'
})

# Now join with df1 (boro, zipcode)
final = pd.merge(join_2, df1, on="zipcode")

# The target schema also has 'businesses' column (integer), which is the total businesses count per zipcode.
# This is not directly in any source, but source 5 (training_5.csv) has ['zipcode', 'businesses'] but no counts.
# The prompt says all source tables must be used, so we must load source 5 and join it as well.

df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

final = pd.merge(final, df5, on="zipcode", how="left")

# Rename df5's 'businesses' to 'businesses' in final (already named 'businesses')

# Reorder columns to match target schema:
final = final[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
               'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8',
               'boro', 'businesses']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)