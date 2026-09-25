import pandas as pd

source0_df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_83/test_0.csv', index_col=0)
source1_df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_83/test_1.csv', index_col=0)

source0_df = source0_df.rename(columns={
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

merged_df = pd.merge(source0_df, source1_df, on='Country', validate='one_to_one')

merged_df.to_csv('autopipeline-benchmarks/github-pipelines/length1_83/target_multisource_mcts_recovery_test_val.csv', index=False)