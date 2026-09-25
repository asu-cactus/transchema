import pandas as pd

# Read source tables with index_col=0 to ignore the first numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)

# Rename columns in source1 to match target suffix _15
source1_renamed = source1.rename(columns={
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

# source0 columns already have suffix _17, but rename 'Happiness_Rank_17' and 'Happiness_Score_17' to match target exactly
# Actually, source0 columns match target suffix _17, so no rename needed except ensure column names match exactly
# Just ensure columns are exactly as in target schema

# Join on 'Country'
df_joined = pd.merge(source1_renamed, source0, on='Country', how='inner')

# The target schema has 'Region' from source1, so keep it as is

# Group by 'Country' and 'Region' to ensure uniqueness (no aggregation needed as columns are unique per country)
# But to be safe, drop duplicates after groupby (or just drop duplicates)
df_final = df_joined.drop_duplicates(subset=['Country', 'Region'])

# Reorder columns to match target schema exactly
target_columns = [
    'Country', 'Region',
    'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15',
    'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
    'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17',
    'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'
]

# Some columns in source0 have slightly different names, ensure they match target exactly
# source0 columns: 'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'

# Check if all target columns exist in df_final
missing_cols = set(target_columns) - set(df_final.columns)
if missing_cols:
    raise ValueError(f"Missing columns in final dataframe: {missing_cols}")

df_final = df_final[target_columns]

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)