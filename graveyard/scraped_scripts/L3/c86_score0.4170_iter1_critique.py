import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_2.csv", index_col=0)

# Join Source1 and Source2 on 'Country'
join_1_2 = pd.merge(source1, source2, on='Country', how='inner')

# Prepare Source0 for pivot: years 2006-2015
years = [str(y) for y in range(2006, 2016)]

# Melt Source0 to long format for years 2006-2015
source0_years = source0[['Country Name', 'Indicator Name'] + years].melt(
    id_vars=['Country Name', 'Indicator Name'],
    value_vars=years,
    var_name='Year',
    value_name='Value'
)

# Pivot to get indicators as columns with years as sub-columns
pivot_full = source0_years.pivot_table(
    index='Country Name',
    columns=['Indicator Name', 'Year'],
    values='Value'
)

# Flatten multiindex columns
pivot_full.columns = [f"{ind} {year}" for ind, year in pivot_full.columns]
pivot_full = pivot_full.reset_index()

# Identify the indicator with most non-null values for years 2006-2015
year_cols = [col for col in pivot_full.columns if col != 'Country Name']
indicators_in_pivot = set(col.rsplit(' ', 1)[0] for col in year_cols)

indicator_counts = {}
for ind in indicators_in_pivot:
    cols = [f"{ind} {year}" for year in years if f"{ind} {year}" in pivot_full.columns]
    count = pivot_full[cols].notnull().sum().sum()
    indicator_counts[ind] = count

best_indicator = max(indicator_counts, key=indicator_counts.get)

# Extract year columns for best indicator and rename to just years
year_data = pivot_full[['Country Name'] + [f"{best_indicator} {year}" for year in years]].rename(
    columns={f"{best_indicator} {year}": year for year in years}
)

# Join the combined Source1+Source2 with Source0 pivoted data on Country = Country Name
full_join = pd.merge(join_1_2, year_data, left_on='Country', right_on='Country Name', how='inner')

# Now group by 'Rank' to ensure uniqueness and aggregate numeric columns
# Define aggregation functions:
# Sum for counts and totals, mean for averages (Citations per document, % Renewable)
agg_dict = {
    'Documents': 'sum',
    'Citable documents': 'sum',
    'Citations': 'sum',
    'Self-citations': 'sum',
    'Citations per document': 'mean',
    'H index': 'sum',
    'Energy Supply': 'sum',
    'Energy Supply per Capita': 'sum',
    '% Renewable': 'mean',
}

# Add years columns aggregation as sum
for year in years:
    agg_dict[year] = 'sum'

# Group by 'Rank' and aggregate
grouped = full_join.groupby('Rank', as_index=False).agg(agg_dict)

# After grouping, 'Rank' is unique key, but we lost 'Country' column, which is not needed in target

# Cast columns to integer types as per target schema, rounding where needed
# 'Citations per document' and '% Renewable' are floats, round and convert to Int64
grouped['Citations per document'] = grouped['Citations per document'].round().astype('Int64')
grouped['% Renewable'] = grouped['% Renewable'].round().astype('Int64')

# Cast other columns to Int64
int_cols = ['Documents', 'Citable documents', 'Citations', 'Self-citations', 'H index',
            'Energy Supply', 'Energy Supply per Capita'] + years

for col in int_cols:
    grouped[col] = grouped[col].round().astype('Int64')

# Reorder columns to match target schema exactly
target_columns = ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations',
                  'Citations per document', 'H index', 'Energy Supply', 'Energy Supply per Capita',
                  '% Renewable'] + years

final_result = grouped[target_columns]

# Write output
final_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_86/target_multisource_mcts.csv", index=False)