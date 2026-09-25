import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_83/training_1.csv", index_col=0)

# Rename columns in source0 to match target suffix _15
source0_renamed = source0.rename(columns={
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

# Rename columns in source1 to match target suffix _17
source1_renamed = source1.rename(columns={
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

# Join on 'Country' (inner join to keep only countries present in both)
joined = pd.merge(source0_renamed, source1_renamed, on='Country', how='inner')

# Select and reorder columns to match target schema exactly
final_columns = [
    'Country', 'Region',
    'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15',
    'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
    'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17',
    'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'
]

# Some columns may be missing if source1 has no 'Region' column, but 'Region' is from source0
# So 'Region' is from source0_renamed and preserved in join

# Output final dataframe with exact columns
final_df = joined[final_columns]

# Write to target CSV
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_83/target_multisource_mcts.csv", index=False)