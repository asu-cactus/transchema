import pandas as pd

# Load source tables
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)

# Rename columns in source1 to match target suffix _15 and unify column names for aggregation
source1_renamed = source1.rename(columns={
    'Happiness Rank': 'Happiness_Rank_15',
    'Happiness Score': 'Happiness_Score_15',
    'Standard Error': 'Standard_Error_15',
    'Economy (GDP per Capita)': 'Economy_15',
    'Health (Life Expectancy)': 'Life_Expectancy_15',
    'Trust (Government Corruption)': 'Trust_15',
    'Generosity': 'Generosity_15',
    'Dystopia Residual': 'Dystopia_15',
    'Family': 'Family_15',
    'Freedom': 'Freedom_15'
})

# Group by Country and aggregate mean for numeric columns, keep Region as first non-null value
agg_cols_15 = [col for col in source1_renamed.columns if col not in ['Country', 'Region']]
grouped_15 = source1_renamed.groupby('Country').agg(
    {**{col: 'mean' for col in agg_cols_15},
     'Region': 'first'}
).reset_index()

# Rename columns in source0 to match target suffix _17
source0_renamed = source0.rename(columns={
    'Happiness_Rank_17': 'Happiness_Rank_17',
    'Happiness_Score_17': 'Happiness_Score_17',
    'Whisker_High_17': 'Whisker_High_17',
    'Whisker_Low_17': 'Whisker_Low_17',
    'Economy_17': 'Economy_17',
    'Family_17': 'Family_17',
    'Life_Expectancy_17': 'Life_Expectancy_17',
    'Freedom_17': 'Freedom_17',
    'Generosity_17': 'Generosity_17',
    'Trust_17': 'Trust_17',
    'Dystopia_17': 'Dystopia_17'
})

# Merge the two grouped dataframes on Country
merged = pd.merge(grouped_15, source0_renamed, on='Country', how='inner')

# Reorder and select columns to match target schema
final_columns = [
    'Country', 'Region',
    'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
    'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'
]

result = merged[final_columns]

# Fix data types according to target schema
result['Country'] = result['Country'].astype(str)
result['Region'] = result['Region'].astype(str)
int_cols_15 = ['Happiness_Rank_15']
int_cols_17 = ['Happiness_Rank_17']
for col in int_cols_15:
    result[col] = result[col].round().astype('Int64')
for col in int_cols_17:
    result[col] = result[col].round().astype('Int64')

float_cols = [
    'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
    'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'
]
for col in float_cols:
    result[col] = result[col].astype(float)

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)