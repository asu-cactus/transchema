import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)

agg_df1 = df1.groupby('Region').agg({
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
}).reset_index()

merged = pd.merge(df0, agg_df1, how='inner', left_on='Country', right_on='Region', suffixes=('_17', '_15'))

# Rename columns from agg_df1 to target suffix _15
agg_rename_map = {
    'Region': 'Region',
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
}

# Rename columns from df0 to target suffix _17
df0_rename_map = {
    'Country': 'Country',
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

# The columns in df0 are named as in source, so rename them accordingly
df0_rename_map_source = {
    'Country': 'Country',
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

# Actually df0 columns are:
# ['Country', 'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17']
# So no rename needed except to ensure consistent names (already consistent)

# Rename agg_df1 columns in merged
for src_col, tgt_col in agg_rename_map.items():
    if src_col in merged.columns:
        merged.rename(columns={src_col: tgt_col}, inplace=True)

# Rename df0 columns in merged if needed (they have suffix _17 from merge)
for col in df0.columns:
    col_17 = col
    if col_17 in merged.columns:
        # Already have correct names, no rename needed
        pass

# The merge added columns: 'Region' from agg_df1 and 'Region' from df0? Actually merged on df0.Country = agg_df1.Region
# So 'Region' from agg_df1 is renamed to 'Region' (agg_rename_map), and df0.Region is not present in merged (df0 has no Region column)
# But target schema requires 'Region' column from source1_79_1 (agg_df1), so keep that.

# Select and reorder columns as per target schema
final_cols = [
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
]

# Some columns from df0 have underscores, ensure they exist in merged
# Rename df0 columns to match target columns if needed
df0_rename_for_target = {
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

for old_col, new_col in df0_rename_for_target.items():
    if old_col in merged.columns and old_col != new_col:
        merged.rename(columns={old_col: new_col}, inplace=True)

result = merged[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)