import pandas as pd

# Read source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

# Identify min, max, and median year
min_year = df['year'].min()
max_year = df['year'].max()
median_year = df['year'].median()
# median_year may be float if even number of years, convert to int and pick closest year in data
median_year = int(median_year)
if median_year not in df['year'].unique():
    # pick closest year to median_year
    median_year = df['year'].iloc[(df['year'] - median_year).abs().argsort()[0]]

# Filter for min year and rename columns with _x suffix
df_x = df[df['year'] == min_year].copy()
df_x = df_x[['country', 'NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL']]
df_x.columns = ['country', 'NY.GDP.MKTP.KN_x', 'SI.DST.10TH.10_x', 'SP.POP.TOTL_x']

# Filter for max year and rename columns with _y suffix
df_y = df[df['year'] == max_year].copy()
df_y = df_y[['country', 'NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL']]
df_y.columns = ['country', 'NY.GDP.MKTP.KN_y', 'SI.DST.10TH.10_y', 'SP.POP.TOTL_y']

# Filter for median year and keep original column names
df_m = df[df['year'] == median_year].copy()
df_m = df_m[['country', 'NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL']]

# Join df_x and df_y on country (inner join)
df_joined = pd.merge(df_x, df_y, on='country', how='inner')

# Join the above with df_m on country (inner join)
df_final = pd.merge(df_joined, df_m, on='country', how='inner')

# Reorder columns to match target schema exactly
df_final = df_final[['country',
                     'NY.GDP.MKTP.KN_x', 'SI.DST.10TH.10_x', 'SP.POP.TOTL_x',
                     'NY.GDP.MKTP.KN_y', 'SI.DST.10TH.10_y', 'SP.POP.TOTL_y',
                     'NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL']]

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)