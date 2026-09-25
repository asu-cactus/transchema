import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)  # 2017 data
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)  # 2015 data

# Rename columns in df1 to match target suffix _15
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

# Join on Country to get Region and 2015 data from df1, and 2017 data from df0
merged = pd.merge(df0, df1_renamed, on='Country', how='inner')

# Select and reorder columns to match target schema
result = merged[[
    'Country',
    'Region',
    'Happiness_Rank_15',
    'Happiness_Score_15',
    'Standard_Error_15',
    'Economy_15',
    'Family_15',
    'Life_Expectancy_15',
    'Freedom_15',
    'Trust_15',
    'Generosity_15',
    'Dystopia_15',
    'Happiness_Rank_17',
    'Happiness_Score_17',
    'Whisker_High_17',
    'Whisker_Low_17',
    'Economy_17',
    'Family_17',
    'Life_Expectancy_17',
    'Freedom_17',
    'Generosity_17',
    'Trust_17',
    'Dystopia_17'
]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)