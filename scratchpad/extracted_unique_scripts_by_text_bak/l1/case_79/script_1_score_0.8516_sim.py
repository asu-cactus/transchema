import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv", index_col=0)

g0 = df0.groupby("Country", as_index=False).agg({
    "Happiness_Rank_17": "mean",
    "Happiness_Score_17": "mean",
    "Whisker_High_17": "mean",
    "Whisker_Low_17": "mean",
    "Economy_17": "mean",
    "Family_17": "mean",
    "Life_Expectancy_17": "mean",
    "Freedom_17": "mean",
    "Generosity_17": "mean",
    "Trust_17": "mean",
    "Dystopia_17": "mean"
})

g1 = df1.groupby("Country", as_index=False).agg({
    "Region": "first",
    "Happiness Rank": "mean",
    "Happiness Score": "mean",
    "Standard Error": "mean",
    "Economy (GDP per Capita)": "mean",
    "Family": "mean",
    "Health (Life Expectancy)": "mean",
    "Freedom": "mean",
    "Trust (Government Corruption)": "mean",
    "Generosity": "mean",
    "Dystopia Residual": "mean"
})

g1 = g1.rename(columns={
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

result = pd.merge(g1, g0, on="Country", how="inner")

cols = ['Country', 'Region',
        'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15',
        'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17']

result = result[cols]

result["Happiness_Rank_15"] = result["Happiness_Rank_15"].round().astype("Int64")
result["Happiness_Rank_17"] = result["Happiness_Rank_17"].round().astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv", index=False)