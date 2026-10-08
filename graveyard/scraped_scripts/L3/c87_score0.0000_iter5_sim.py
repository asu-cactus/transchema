import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_2.csv", index_col=0)

grouped = df0.groupby(['Indicator Name', 'Indicator Code'], dropna=False).agg(
    CountryCode_Count=('Country Code', 'count'),
    Sum_2015=('2015', 'sum')
).reset_index()

# Join grouped with df2 on Country = Indicator Name (likely a mismatch, so try join on Indicator Name = Country)
# But target schema is ['Rank', '0'], and target examples show Rank and 0 as integers.
# The partial plan groups by Indicator Name and Code, but target examples show Rank and 0 columns.
# Source2 has Rank and Country columns, so join grouped on Indicator Name = Country to get Rank.
# Then '0' column in target is probably the count of Country Code from grouped.

# Join on grouped['Indicator Name'] == df2['Country']
merged = pd.merge(df2, grouped, left_on='Country', right_on='Indicator Name', how='inner')

# Prepare final dataframe with columns Rank and 0 (0 is count of Country Code)
result = merged[['Rank', 'CountryCode_Count']].copy()
result.rename(columns={'CountryCode_Count': '0'}, inplace=True)

result['Rank'] = result['Rank'].astype(int)
result['0'] = result['0'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_87/target_multisource_mcts.csv", index=False)