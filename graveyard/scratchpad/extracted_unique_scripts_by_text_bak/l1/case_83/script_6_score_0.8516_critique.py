import pandas as pd

# Read source files with index_col=0 to ignore the first index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_1.csv", index_col=0)

# Join on 'Country' only, keep all countries present in both sources (inner join)
merged = pd.merge(df0, df1, on='Country', how='inner')

# Construct the result DataFrame with exact target schema and column names
result = pd.DataFrame({
    'Country': merged['Country'],
    'Region': merged['Region'],
    'Happiness_Rank_15': merged['Happiness Rank'].astype('Int64'),
    'Happiness_Score_15': merged['Happiness Score'].astype(float),
    'Standard_Error_15': merged['Standard Error'].astype(float),
    'Economy_15': merged['Economy (GDP per Capita)'].astype(float),
    'Family_15': merged['Family'].astype(float),
    'Life_Expectancy_15': merged['Health (Life Expectancy)'].astype(float),
    'Freedom_15': merged['Freedom'].astype(float),
    'Trust_15': merged['Trust (Government Corruption)'].astype(float),
    'Generosity_15': merged['Generosity'].astype(float),
    'Dystopia_15': merged['Dystopia Residual'].astype(float),
    'Happiness_Rank_17': merged['Happiness_Rank_17'].astype('Int64'),
    'Happiness_Score_17': merged['Happiness_Score_17'].astype(float),
    'Whisker_High_17': merged['Whisker_High_17'].astype(float),
    'Whisker_Low_17': merged['Whisker_Low_17'].astype(float),
    'Economy_17': merged['Economy_17'].astype(float),
    'Family_17': merged['Family_17'].astype(float),
    'Life_Expectancy_17': merged['Life_Expectancy_17'].astype(float),
    'Freedom_17': merged['Freedom_17'].astype(float),
    'Generosity_17': merged['Generosity_17'].astype(float),
    'Trust_17': merged['Trust_17'].astype(float),
    'Dystopia_17': merged['Dystopia_17'].astype(float)
})

# Write output to the specified path without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_83/target_multisource_mcts.csv", index=False)