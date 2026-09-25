import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)

agg = df1.groupby(['Country', 'Region'], as_index=False).agg({
    'Happiness Rank': 'min',
    'Happiness Score': 'min',
    'Standard Error': 'min',
    'Economy (GDP per Capita)': 'min',
    'Family': 'max',
    'Health (Life Expectancy)': 'min',
    'Freedom': 'min',
    'Trust (Government Corruption)': 'max',
    'Generosity': 'max',
    'Dystopia Residual': 'min'
})

agg = agg.rename(columns={
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

df0_renamed = df0.rename(columns={
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

# Actually, df0 columns are: ['Country', 'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17']
# So rename columns to match target schema exactly:
df0_renamed = df0.rename(columns={
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

# Join on Country
merged = pd.merge(agg, df0_renamed, on='Country', how='inner')

# Rename columns to target schema names exactly
merged = merged.rename(columns={
    'Region': 'Region',
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

# Reorder columns to match target schema exactly
final_columns = [
    'Country', 'Region',
    'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
    'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'
]

result = merged[final_columns]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)