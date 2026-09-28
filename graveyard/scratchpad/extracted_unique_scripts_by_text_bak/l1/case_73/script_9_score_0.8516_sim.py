import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_1.csv", index_col=0)

df0.columns = [col.strip() for col in df0.columns]
df1.columns = [col.strip() for col in df1.columns]

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

df_merged = pd.merge(df1_renamed, df0, how='inner', on='Country')

cols_order = [
    'Country', 'Region',
    'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
    'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'
]

df_final = df_merged[cols_order]

df_final['Happiness_Rank_15'] = df_final['Happiness_Rank_15'].astype('Int64')
df_final['Happiness_Rank_17'] = df_final['Happiness_Rank_17'].astype('Int64')

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_73/target_multisource_mcts.csv", index=False)