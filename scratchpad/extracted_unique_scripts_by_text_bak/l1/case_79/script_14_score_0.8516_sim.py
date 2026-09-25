import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_79/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_79/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg_df1 = df1.groupby('Country').agg({
    'Happiness Rank': 'mean',
    'Happiness Score': 'mean',
    'Standard Error': 'mean',
    'Economy (GDP per Capita)': 'mean',
    'Family': 'mean',
    'Health (Life Expectancy)': 'mean',
    'Freedom': 'mean',
    'Trust (Government Corruption)': 'mean',
    'Generosity': 'mean',
    'Dystopia Residual': 'mean',
    'Region': 'first'
}).reset_index()

merged = pd.merge(agg_df1, df0, on='Country', how='inner')

merged = merged.rename(columns={
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
    'Dystopia_17': 'Dystopia_17',
    'Region': 'Region'
})

final_cols = ['Country', 'Region', 'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15', 'Happiness_Rank_17', 'Happiness_Score_17', 'Whisker_High_17', 'Whisker_Low_17', 'Economy_17', 'Family_17', 'Life_Expectancy_17', 'Freedom_17', 'Generosity_17', 'Trust_17', 'Dystopia_17']

result = merged[final_cols]

result.to_csv(target_path, index=False)