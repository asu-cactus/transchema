import pandas as pd

# Read source files with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)

# Rename columns in df0 to match target schema suffix _17
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

# Rename columns in df1 to match target schema suffix _15
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

# Join on 'Country' with left join to keep all countries from df1 (which has Region)
df_merged = pd.merge(df1, df0, on='Country', how='left')

# Define columns for group by and aggregation
group_by_cols = ['Country', 'Region']

# Columns to take first (integers and strings)
first_cols = ['Happiness_Rank_15', 'Happiness_Rank_17']

# Columns to aggregate by mean (floats)
mean_cols = [
    'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15',
    'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
    'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17',
    'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'
]

# Aggregate dictionary
agg_dict = {}

for col in first_cols:
    agg_dict[col] = 'first'

for col in mean_cols:
    agg_dict[col] = 'mean'

# Perform group by aggregation
df_final = df_merged.groupby(group_by_cols, as_index=False).agg(agg_dict)

# Convert integer columns to Int64 dtype to match target schema
df_final['Happiness_Rank_15'] = df_final['Happiness_Rank_15'].astype('Int64')
df_final['Happiness_Rank_17'] = df_final['Happiness_Rank_17'].astype('Int64')

# Reorder columns to match target schema exactly
final_columns = [
    'Country', 'Region',
    'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15',
    'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
    'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17',
    'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'
]

df_final = df_final[final_columns]

# Write to CSV without index
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)