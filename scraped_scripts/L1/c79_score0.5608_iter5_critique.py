import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)

# Rename columns in df1 to match target schema suffix _15
df1.rename(columns={
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

# Rename columns in df0 to match target schema suffix _17 (already matching, but ensure)
df0.rename(columns={
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

# Join on 'Country' with outer join to keep all countries
df_merged = pd.merge(df1, df0, on='Country', how='outer')

# Select columns in target order
cols = ['Country', 'Region',
        'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
        'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17']

df_selected = df_merged[cols]

# Group by ['Country', 'Region'] and aggregate numeric columns by mean
group_by_cols = ['Country', 'Region']
agg_cols = [col for col in cols if col not in group_by_cols]

df_final = df_selected.groupby(group_by_cols, dropna=False, as_index=False)[agg_cols].mean()

# Convert rank columns back to Int64 (nullable integer)
df_final['Happiness_Rank_15'] = df_final['Happiness_Rank_15'].round().astype('Int64')
df_final['Happiness_Rank_17'] = df_final['Happiness_Rank_17'].round().astype('Int64')

# Write to CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)