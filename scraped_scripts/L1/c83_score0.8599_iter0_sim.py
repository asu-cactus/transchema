import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_1.csv", index_col=0)

agg_cols_0 = {
    'Happiness Rank': 'mean',
    'Happiness Score': 'mean',
    'Standard Error': 'mean',
    'Economy (GDP per Capita)': 'mean',
    'Family': 'mean',
    'Health (Life Expectancy)': 'mean',
    'Freedom': 'mean',
    'Trust (Government Corruption)': 'mean',
    'Generosity': 'mean',
    'Dystopia Residual': 'mean'
}

df0_agg = df0.groupby(['Country', 'Region'], as_index=False).agg(agg_cols_0)

df_merged = pd.merge(df0_agg, df1, on='Country', how='inner')

df_merged.rename(columns={
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

df_merged = df_merged[['Country', 'Region',
                       'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
                       'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17']]

df_merged['Happiness_Rank_15'] = df_merged['Happiness_Rank_15'].round().astype('Int64')
df_merged['Happiness_Rank_17'] = df_merged['Happiness_Rank_17'].astype('Int64')

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_83/target_multisource_mcts.csv", index=False)