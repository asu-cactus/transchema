import pandas as pd

# Load source 0 with year 2017 data
source0 = pd.read_csv(
    'autopipeline-benchmarks/github-pipelines/length1_73/test_0.csv',
    index_col=0
)

# Load source 1 with year 2015 data and rename columns
source1 = pd.read_csv(
    'autopipeline-benchmarks/github-pipelines/length1_73/test_1.csv',
    index_col=0
).rename(columns={
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

# Merge the two sources on Country
merged_df = pd.merge(source0, source1, on='Country', how='inner')

# Save the result to target file
merged_df.to_csv(
    'autopipeline-benchmarks/github-pipelines/length1_73/target_multisource_mcts_recovery_test_val.csv',
    index=False
)