import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_1.csv", index_col=0)

agg_df1 = df1.groupby(['Country', 'Region'], as_index=False).agg({
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
})

merged = pd.merge(agg_df1, df0, on='Country', how='inner')

result = pd.DataFrame()
result['Country'] = merged['Country']
result['Region'] = merged['Region']
result['Happiness_Rank_15'] = merged['Happiness Rank'].astype('Int64')
result['Happiness_Score_15'] = merged['Happiness Score']
result['Standard_Error_15'] = merged['Standard Error']
result['Economy_15'] = merged['Economy (GDP per Capita)']
result['Family_15'] = merged['Family']
result['Life_Expectancy_15'] = merged['Health (Life Expectancy)']
result['Freedom_15'] = merged['Freedom']
result['Trust_15'] = merged['Trust (Government Corruption)']
result['Generosity_15'] = merged['Generosity']
result['Dystopia_15'] = merged['Dystopia Residual']
result['Happiness_Rank_17'] = merged['Happiness_Rank_17'].astype('Int64')
result['Happiness_Score_17'] = merged['Happiness_Score_17']
result['Whisker_High_17'] = merged['Whisker_High_17']
result['Whisker_Low_17'] = merged['Whisker_Low_17']
result['Economy_17'] = merged['Economy_17']
result['Family_17'] = merged['Family_17']
result['Life_Expectancy_17'] = merged['Life_Expectancy_17']
result['Freedom_17'] = merged['Freedom_17']
result['Generosity_17'] = merged['Generosity_17']
result['Trust_17'] = merged['Trust_17']
result['Dystopia_17'] = merged['Dystopia_17']

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_73/target_multisource_mcts.csv", index=False)