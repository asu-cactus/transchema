import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_2.csv", index_col=0)

join1 = pd.merge(source0, source1, on="Athlete", how="inner")
join2 = pd.merge(join1, source2, on="Athlete", how="inner")
final_join = pd.merge(join2, source0, on="Athlete", how="inner", suffixes=('', '_dup'))

final = final_join[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country', 'Sport']]

final['Age'] = final['Age'].astype(float)
final['Year'] = final['Year'].astype(int)
final['Gold Medals'] = final['Gold Medals'].astype(int)
final['Silver Medals'] = final['Silver Medals'].astype(int)
final['Bronze Medals'] = final['Bronze Medals'].astype(int)
final['Total Medals'] = final['Total Medals'].astype(int)
final['Closing Ceremony Date'] = final['Closing Ceremony Date'].astype(str)
final['Country'] = final['Country'].astype(str)
final['Sport'] = final['Sport'].astype(str)

final.to_csv("autopipeline-benchmarks/github-pipelines/length2_53/target_multisource_mcts.csv", index=False)