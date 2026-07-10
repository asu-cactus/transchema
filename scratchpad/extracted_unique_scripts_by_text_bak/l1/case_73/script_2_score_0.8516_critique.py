import pandas as pd

# Read source tables
df_17 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_0.csv", index_col=0)
df_15 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_1.csv", index_col=0)

# Rename columns in df_15 to match target suffix _15
df_15_renamed = df_15.rename(columns={
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

# Aggregate df_15 by Country and Region, taking mean of numeric columns, first of Region (Region is kept as group key)
agg_15 = df_15_renamed.groupby(["Country", "Region"], as_index=False).agg({
    "Happiness_Rank_15": "mean",
    "Happiness_Score_15": "mean",
    "Standard_Error_15": "mean",
    "Economy_15": "mean",
    "Family_15": "mean",
    "Life_Expectancy_15": "mean",
    "Freedom_15": "mean",
    "Trust_15": "mean",
    "Generosity_15": "mean",
    "Dystopia_15": "mean"
})

# Rename columns in df_17 to match target suffix _17 (no change needed except for consistency)
df_17_renamed = df_17.rename(columns={
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

# Merge on Country only (Region only exists in df_15)
result = pd.merge(agg_15, df_17_renamed, on="Country", how="inner")

# Reorder columns to match target schema exactly
result = result[[
    "Country", "Region",
    "Happiness_Rank_15", "Happiness_Score_15", "Standard_Error_15", "Economy_15", "Family_15", "Life_Expectancy_15", "Freedom_15", "Trust_15", "Generosity_15", "Dystopia_15",
    "Happiness_Rank_17", "Happiness_Score_17", "Whisker_High_17", "Whisker_Low_17", "Economy_17", "Family_17", "Life_Expectancy_17", "Freedom_17", "Generosity_17", "Trust_17", "Dystopia_17"
]]

# Convert rank columns to integer type (nullable Int64)
result["Happiness_Rank_15"] = result["Happiness_Rank_15"].round().astype("Int64")
result["Happiness_Rank_17"] = result["Happiness_Rank_17"].round().astype("Int64")

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_73/target_multisource_mcts.csv", index=False)