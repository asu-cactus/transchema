import pandas as pd

# Read source files with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_1.csv", index_col=0)

# Group Source0 by Country and Region to ensure uniqueness, aggregate other columns by 'first'
agg_15 = {
    'Happiness Rank': 'first',
    'Happiness Score': 'first',
    'Standard Error': 'first',
    'Economy (GDP per Capita)': 'first',
    'Family': 'first',
    'Health (Life Expectancy)': 'first',
    'Freedom': 'first',
    'Trust (Government Corruption)': 'first',
    'Generosity': 'first',
    'Dystopia Residual': 'first'
}

df0_agg = df0.groupby(['Country', 'Region'], as_index=False).agg(agg_15)

# Rename columns in df0 to match target schema suffix _15
df0_agg = df0_agg.rename(columns={
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
})

# Rename columns in df1 to match target schema (already mostly matching)
df1_renamed = df1.rename(columns={
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

# Join on 'Country' only, inner join to keep only countries present in both
df_merged = pd.merge(df0_agg, df1_renamed, on='Country', how='inner')

# Reorder columns to match target schema exactly
df_merged = df_merged[['Country', 'Region', 'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15',
                       'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
                       'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17',
                       'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17']]

# Convert rank columns to integer type with nullable Int64 dtype
df_merged['Happiness_Rank_15'] = df_merged['Happiness_Rank_15'].astype('Int64')
df_merged['Happiness_Rank_17'] = df_merged['Happiness_Rank_17'].astype('Int64')

# Write output CSV without index
df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_83/target_multisource_mcts.csv", index=False)