import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_2.csv", index_col=0)

# Join source1 (main event info) with source0 (Sport) on Athlete
join1 = pd.merge(source1, source0, on="Athlete", how="inner")

# Join the above result with source2 (Country) on Athlete
join2 = pd.merge(join1, source2, on="Athlete", how="inner")

# Group by the leftmost columns that uniquely identify rows in target
group_cols = ['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Country', 'Sport']
agg_cols = ['Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals']

final = join2.groupby(group_cols, as_index=False)[agg_cols].sum()

# Ensure correct dtypes as per target schema
final['Age'] = final['Age'].astype(float)
final['Year'] = final['Year'].astype(int)
final['Gold Medals'] = final['Gold Medals'].astype(int)
final['Silver Medals'] = final['Silver Medals'].astype(int)
final['Bronze Medals'] = final['Bronze Medals'].astype(int)
final['Total Medals'] = final['Total Medals'].astype(int)
final['Closing Ceremony Date'] = final['Closing Ceremony Date'].astype(str)
final['Country'] = final['Country'].astype(str)
final['Sport'] = final['Sport'].astype(str)

final = final[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country', 'Sport']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length2_53/target_multisource_mcts.csv", index=False)