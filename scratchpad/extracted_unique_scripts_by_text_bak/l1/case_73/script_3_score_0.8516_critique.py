import pandas as pd

# Read source tables with index_col=0 to ignore the first numerical index column
source0_path = "autopipeline-benchmarks/github-pipelines/length1_73/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_73/training_1.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on 'Country' (common key)
df_joined = pd.merge(df1, df0, on="Country", how="inner")

# Rename columns to match target schema exactly
# Source1_73_1 columns to target suffix _15
rename_map_15 = {
    'Happiness Rank': 'Happiness_Rank_15',
    'Happiness Score': 'Happiness_Score_15',
    'Standard Error': 'Standard_Error_15',
    'Economy (GDP per Capita)': 'Economy_15',
    'Family': 'Family_15',
    'Health (Life Expectancy)': 'Life_Expectancy_15',
    'Freedom': 'Freedom_15',
    'Trust (Government Corruption)': 'Trust_15',
    'Generosity': 'Generosity_15',
    'Dystopia Residual': 'Dystopia_15',
    'Region': 'Region'
}

# Source1_73_0 columns already have suffix _17, but some columns need to be renamed to match target exactly
rename_map_17 = {
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
}

# Rename columns from df1 (source1_73_1)
df_joined = df_joined.rename(columns=rename_map_15)

# Columns from df0 are already named correctly, no rename needed for them except ensure no duplicates
# But to be safe, rename columns from df0 to target names (some columns have underscores, so just keep as is)
df_joined = df_joined.rename(columns=rename_map_17)

# Select columns in the exact order of target schema
target_columns = [
    'Country', 'Region',
    'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15',
    'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
    'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17',
    'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17'
]

df_final = df_joined[target_columns]

# Write to output CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_73/target_multisource_mcts.csv", index=False)