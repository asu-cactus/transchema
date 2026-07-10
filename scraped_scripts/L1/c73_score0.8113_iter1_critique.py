import pandas as pd

# Read source files with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_1.csv", index_col=0)

# Rename columns in df0 (2017 data) to match target schema suffix _17
df0.rename(columns={
    'Country': 'Country',
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
}, inplace=True)

# Rename columns in df1 (2015 data) to match target schema suffix _15
df1.rename(columns={
    'Country': 'Country',
    'Region': 'Region',
    'Happiness Rank': 'Happiness_Rank_15',
    'Happiness Score': 'Happiness_Score_15',
    'Standard Error': 'Standard_Error_15',
    'Economy (GDP per Capita)': 'Economy_15',
    'Family': 'Family_15',
    'Health (Life Expectancy)': 'Life_Expectancy_15',
    'Freedom': 'Freedom_15',
    'Trust (Government Corruption)': 'Trust_15',
    'Generosity': 'Generosity_15',
    'Dystopia Residual': 'Dystopia_15'
}, inplace=True)

# Join on 'Country' with left join to keep all countries from df1 (2015 data)
df = pd.merge(df1, df0, on='Country', how='left')

# Select columns in target schema order
cols = ['Country', 'Region',
        'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
        'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17']

df = df[cols]

# Group by 'Country' and 'Region' to ensure unique rows
# For integer columns (ranks), use first (since ranks should be unique per country)
# For float columns, use mean aggregation

# Identify integer columns (ranks)
int_cols = ['Happiness_Rank_15', 'Happiness_Rank_17']
# All other columns except 'Country' and 'Region' are floats
float_cols = [c for c in cols if c not in ['Country', 'Region'] + int_cols]

agg_dict = {}
for c in int_cols:
    agg_dict[c] = 'first'
for c in float_cols:
    agg_dict[c] = 'mean'

df = df.groupby(['Country', 'Region'], as_index=False).agg(agg_dict)

# Convert rank columns to integer type (nullable Int64)
df['Happiness_Rank_15'] = df['Happiness_Rank_15'].astype('Int64')
df['Happiness_Rank_17'] = df['Happiness_Rank_17'].astype('Int64')

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_73/target_multisource_mcts.csv", index=False)