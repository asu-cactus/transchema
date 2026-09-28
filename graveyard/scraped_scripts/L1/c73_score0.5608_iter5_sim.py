import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_1.csv", index_col=0)

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

df1_renamed = df1.rename(columns={
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

df1_renamed = df1_renamed[[
    'Country', 'Region', 'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15',
    'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15',
    'Generosity_15', 'Dystopia_15'
]]

df0_renamed = df0_renamed[['Country', 'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17',
                           'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17',
                           'Trust_17', 'Dystopia_17']]

df_merged = pd.merge(df1_renamed, df0_renamed, on='Country', how='outer')

df_merged = df_merged.groupby('Country', as_index=False).agg({
    'Region': 'first',
    'Happiness_Rank_15': 'first',
    'Happiness_Score_15': 'first',
    'Standard_Error_15': 'first',
    'Economy_15': 'first',
    'Family_15': 'first',
    'Life_Expectancy_15': 'first',
    'Freedom_15': 'first',
    'Trust_15': 'first',
    'Generosity_15': 'first',
    'Dystopia_15': 'first',
    'Happiness_Rank_17': 'first',
    'Happiness_Score_17': 'first',
    'Whisker_High_17': 'first',
    'Whisker_Low_17': 'first',
    'Economy_17': 'first',
    'Family_17': 'first',
    'Life_Expectancy_17': 'first',
    'Freedom_17': 'first',
    'Generosity_17': 'first',
    'Trust_17': 'first',
    'Dystopia_17': 'first'
})

df_merged = df_merged[[
    'Country', 'Region', 'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15',
    'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15',
    'Generosity_15', 'Dystopia_15', 'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17',
    'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17',
    'Generosity_17', 'Trust_17', 'Dystopia_17'
]]

df_merged['Happiness_Rank_15'] = df_merged['Happiness_Rank_15'].astype('Int64')
df_merged['Happiness_Rank_17'] = df_merged['Happiness_Rank_17'].astype('Int64')

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_73/target_multisource_mcts.csv", index=False)