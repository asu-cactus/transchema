import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)

df0 = df0.rename(columns={
    "Happiness Rank": "Happiness_Rank_15",
    "Happiness Score": "Happiness_Score_15",
    "Standard Error": "Standard_Error_15",
    "Economy (GDP per Capita)": "Economy_15",
    "Health (Life Expectancy)": "Life_Expectancy_15",
    "Trust (Government Corruption)": "Trust_15",
    "Generosity": "Generosity_15",
    "Dystopia Residual": "Dystopia_15"
})

df_merged = pd.merge(df0, df1, on="Country", how="outer")

df_merged = df_merged[[
    "Country", "Region",
    "Happiness_Rank_15", "Happiness_Score_15", "Standard_Error_15", "Economy_15", "Family", "Life_Expectancy_15", "Freedom", "Trust_15", "Generosity_15", "Dystopia_15",
    "Happiness_Rank_17", "Happiness_Score_17", "Whisker_High_17", "Whisker_Low_17", "Economy_17", "Family_17", "Life_Expectancy_17", "Freedom_17", "Generosity_17", "Trust_17", "Dystopia_17"
]]

df_merged = df_merged.rename(columns={
    "Family": "Family_15",
    "Freedom": "Freedom_15"
})

df_merged = df_merged.astype({
    "Happiness_Rank_15": "Int64",
    "Happiness_Score_15": float,
    "Standard_Error_15": float,
    "Economy_15": float,
    "Family_15": float,
    "Life_Expectancy_15": float,
    "Freedom_15": float,
    "Trust_15": float,
    "Generosity_15": float,
    "Dystopia_15": float,
    "Happiness_Rank_17": "Int64",
    "Happiness_Score_17": float,
    "Whisker_High_17": float,
    "Whisker_Low_17": float,
    "Economy_17": float,
    "Family_17": float,
    "Life_Expectancy_17": float,
    "Freedom_17": float,
    "Generosity_17": float,
    "Trust_17": float,
    "Dystopia_17": float
})

df_merged = df_merged.groupby(["Country", "Region"], as_index=False).first()

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)