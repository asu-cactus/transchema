import pandas as pd

# Read source files with index_col=0 as instructed
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)

# Rename columns in df1 to match target schema for 2015 data
df1 = df1.rename(columns={
    "Happiness Rank": "Happiness_Rank_15",
    "Happiness Score": "Happiness_Score_15",
    "Standard Error": "Standard_Error_15",
    "Economy (GDP per Capita)": "Economy_15",
    "Family": "Family_15",
    "Health (Life Expectancy)": "Life_Expectancy_15",
    "Freedom": "Freedom_15",
    "Trust (Government Corruption)": "Trust_15",
    "Generosity": "Generosity_15",
    "Dystopia Residual": "Dystopia_15"
})

# Join on 'Country' (inner join)
result = pd.merge(df1, df0, on="Country", how="inner")

# Rename columns in df0 to match target schema for 2017 data
result = result.rename(columns={
    "Happiness_Rank_17": "Happiness_Rank_17",
    "Happiness_Score_17": "Happiness_Score_17",
    "Whisker_High_17": "Whisker_High_17",
    "Whisker_Low_17": "Whisker_Low_17",
    "Economy_17": "Economy_17",
    "Family_17": "Family_17",
    "Life_Expectancy_17": "Life_Expectancy_17",
    "Freedom_17": "Freedom_17",
    "Generosity_17": "Generosity_17",
    "Trust_17": "Trust_17",
    "Dystopia_17": "Dystopia_17"
})

# Select and reorder columns exactly as in target schema
cols = ['Country', 'Region',
        'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
        'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17']

result = result[cols]

# Convert rank columns to integer type as in target
result["Happiness_Rank_15"] = result["Happiness_Rank_15"].round().astype("Int64")
result["Happiness_Rank_17"] = result["Happiness_Rank_17"].round().astype("Int64")

# Write output CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)