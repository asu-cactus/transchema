import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_73/training_1.csv", index_col=0)

agg0 = df0.groupby("Country", as_index=False).agg({
    "Happiness_Rank_17": "first",
    "Happiness_Score_17": "first",
    "Whisker_High_17": "first",
    "Whisker_Low_17": "first",
    "Economy_17": "first",
    "Family_17": "first",
    "Life_Expectancy_17": "first",
    "Freedom_17": "first",
    "Generosity_17": "first",
    "Trust_17": "first",
    "Dystopia_17": "first"
})

agg1 = df1.groupby("Country", as_index=False).agg({
    "Region": "first",
    "Happiness Rank": "first",
    "Happiness Score": "first",
    "Standard Error": "first",
    "Economy (GDP per Capita)": "first",
    "Family": "first",
    "Health (Life Expectancy)": "first",
    "Freedom": "first",
    "Trust (Government Corruption)": "first",
    "Generosity": "first",
    "Dystopia Residual": "first"
})

agg1 = agg1.rename(columns={
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

result = pd.merge(agg1, agg0, on="Country", how="inner")

result = result[[
    "Country", "Region",
    "Happiness_Rank_15", "Happiness_Score_15", "Standard_Error_15", "Economy_15", "Family_15", "Life_Expectancy_15", "Freedom_15", "Trust_15", "Generosity_15", "Dystopia_15",
    "Happiness_Rank_17", "Happiness_Score_17", "Whisker_High_17", "Whisker_Low_17", "Economy_17", "Family_17", "Life_Expectancy_17", "Freedom_17", "Generosity_17", "Trust_17", "Dystopia_17"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_73/target_multisource_mcts.csv", index=False)