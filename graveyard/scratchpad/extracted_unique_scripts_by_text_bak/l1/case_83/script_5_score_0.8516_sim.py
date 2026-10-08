import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_1.csv", index_col=0)

agg0 = df0.groupby(['Country', 'Region'], as_index=False).agg({
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

merged = pd.merge(agg0, df1, on='Country', how='inner')

result = pd.DataFrame()
result['Country'] = merged['Country']
result['Region'] = merged['Region']
result['Happiness_Rank_15'] = merged['Happiness Rank'].astype('Int64')
result['Happiness_Score_15'] = merged['Happiness Score'].astype(float)
result['Standard_Error_15'] = merged['Standard Error'].astype(float)
result['Economy_15'] = merged['Economy (GDP per Capita)'].astype(float)
result['Family_15'] = merged['Family'].astype(float)
result['Life_Expectancy_15'] = merged['Health (Life Expectancy)'].astype(float)
result['Freedom_15'] = merged['Freedom'].astype(float)
result['Trust_15'] = merged['Trust (Government Corruption)'].astype(float)
result['Generosity_15'] = merged['Generosity'].astype(float)
result['Dystopia_15'] = merged['Dystopia Residual'].astype(float)
result['Happiness_Rank_17'] = merged['Happiness_Rank_17'].astype('Int64')
result['Happiness_Score_17'] = merged['Happiness_Score_17'].astype(float)
result['Whisker_High_17'] = merged['Whisker_High_17'].astype(float)
result['Whisker_Low_17'] = merged['Whisker_Low_17'].astype(float)
result['Economy_17'] = merged['Economy_17'].astype(float)
result['Family_17'] = merged['Family_17'].astype(float)
result['Life_Expectancy_17'] = merged['Life_Expectancy_17'].astype(float)
result['Freedom_17'] = merged['Freedom_17'].astype(float)
result['Generosity_17'] = merged['Generosity_17'].astype(float)
result['Trust_17'] = merged['Trust_17'].astype(float)
result['Dystopia_17'] = merged['Dystopia_17'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_83/target_multisource_mcts.csv", index=False)