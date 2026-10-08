import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_2.csv", index_col=0)

pivot_df = source0.pivot(index='Country Name', columns='Indicator Name', values='2015').reset_index()

# The pivot above only gets 2015 values, but target needs 2006-2015 columns.
# So pivot all years from 2006 to 2015 for each indicator.

years = [str(y) for y in range(2006, 2016)]
indicators = source0['Indicator Name'].unique()

# Filter source0 for years 2006-2015 only
source0_filtered = source0[['Country Name', 'Indicator Name'] + years]

# Melt years to long format for pivot
melted = source0_filtered.melt(id_vars=['Country Name', 'Indicator Name'], value_vars=years, var_name='Year', value_name='Value')

pivot_full = melted.pivot_table(index='Country Name', columns=['Indicator Name', 'Year'], values='Value')

# Flatten multiindex columns
pivot_full.columns = [f"{ind} {year}" for ind, year in pivot_full.columns]
pivot_full = pivot_full.reset_index()

# We want to keep only the years 2006-2015 as separate columns, so we will keep them as is.

# Now join source1 on Country (source1.Country) = pivot_full['Country Name']
join1 = pd.merge(source1, pivot_full, left_on='Country', right_on='Country Name', how='inner')

# Join source2 on Country
join2 = pd.merge(join1, source2, left_on='Country', right_on='Country', how='inner')

# Now build the final dataframe with the target schema:
# ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index',
#  'Energy Supply', 'Energy Supply per Capita', '% Renewable', '2006', '2007', '2008', '2009', '2010', '2011',
#  '2012', '2013', '2014', '2015']

# Extract year columns from pivot_full columns, but they are named like 'GDP at market prices (constant 2010 US$) 2006'
# We need to find the correct indicator for each year column. The target schema expects years as columns with integer values.

# The target years columns are just years as integers, so we need to pick the correct indicator for these years.
# The source0 indicators are various, but target years columns are just years, so likely the values are from one indicator.
# The prompt does not specify which indicator to use for years columns, but since the target schema has years as columns,
# and source0 has multiple indicators, we must pick the indicator that matches the years columns in the target.

# The target years columns are likely from the indicator "GDP at market prices (constant 2010 US$)" or similar.
# But since the target examples have all 1s, we cannot guess. We will pick the first indicator for years columns.

# Instead, the target schema has years columns as integers, so we will pick the indicator with numeric values for years 2006-2015.
# Let's pick the indicator with the most non-null values for years 2006-2015.

# Find indicator prefixes in pivot_full columns
year_cols = [col for col in pivot_full.columns if col != 'Country Name']
indicators_in_pivot = set(col.rsplit(' ', 1)[0] for col in year_cols)

# For each indicator, count non-null values in years 2006-2015
indicator_counts = {}
for ind in indicators_in_pivot:
    cols = [f"{ind} {year}" for year in years if f"{ind} {year}" in pivot_full.columns]
    count = pivot_full[cols].notnull().sum().sum()
    indicator_counts[ind] = count

# Pick indicator with max count
best_indicator = max(indicator_counts, key=indicator_counts.get)

# Extract columns for best indicator and rename to years only
year_data = pivot_full[['Country Name'] + [f"{best_indicator} {year}" for year in years]]
year_data = year_data.rename(columns={f"{best_indicator} {year}": year for year in years})

# Merge year_data with join2 on Country Name / Country
final = pd.merge(join2, year_data, left_on='Country', right_on='Country Name', how='inner')

# Select and rename columns to target schema
final_result = pd.DataFrame()
final_result['Rank'] = final['Rank'].astype('Int64')
final_result['Documents'] = final['Documents'].astype('Int64')
final_result['Citable documents'] = final['Citable documents'].astype('Int64')
final_result['Citations'] = final['Citations'].astype('Int64')
final_result['Self-citations'] = final['Self-citations'].astype('Int64')

# Citations per document and H index are float and int respectively in source1, convert accordingly
final_result['Citations per document'] = final['Citations per document'].round().astype('Int64')
final_result['H index'] = final['H index'].astype('Int64')

final_result['Energy Supply'] = final['Energy Supply'].astype('Int64')
final_result['Energy Supply per Capita'] = final['Energy Supply per Capita'].astype('Int64')
final_result['% Renewable'] = final['% Renewable'].round().astype('Int64')

for year in years:
    final_result[year] = final[year].round().astype('Int64')

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_86/target_multisource_mcts.csv", index=False)