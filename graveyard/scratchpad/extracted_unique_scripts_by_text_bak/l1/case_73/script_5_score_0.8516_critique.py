import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_1.csv", index_col=0)

# Join on 'Country' only, inner join to keep only matching countries
merged = pd.merge(df1, df0, on='Country', how='inner')

# Construct the result DataFrame with exact target schema and column names
result = pd.DataFrame({
    'Country': merged['Country'],
    'Region': merged['Region'],
    'Happiness_Rank_15': merged['Happiness Rank'].astype('Int64'),
    'Happiness_Score_15': merged['Happiness Score'],
    'Standard_Error_15': merged['Standard Error'],
    'Economy_15': merged['Economy (GDP per Capita)'],
    'Family_15': merged['Family'],
    'Life_Expectancy_15': merged['Health (Life Expectancy)'],
    'Freedom_15': merged['Freedom'],
    'Trust_15': merged['Trust (Government Corruption)'],
    'Generosity_15': merged['Generosity'],
    'Dystopia_15': merged['Dystopia Residual'],
    'Happiness_Rank_17': merged['Happiness_Rank_17'].astype('Int64'),
    'Happiness_Score_17': merged['Happiness_Score_17'],
    'Whisker_High_17': merged['Whisker_High_17'],
    'Whisker_Low_17': merged['Whisker_Low_17'],
    'Economy_17': merged['Economy_17'],
    'Family_17': merged['Family_17'],
    'Life_Expectancy_17': merged['Life_Expectancy_17'],
    'Freedom_17': merged['Freedom_17'],
    'Generosity_17': merged['Generosity_17'],
    'Trust_17': merged['Trust_17'],
    'Dystopia_17': merged['Dystopia_17']
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_73/target_multisource_mcts.csv", index=False)