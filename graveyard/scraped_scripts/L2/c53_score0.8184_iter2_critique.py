import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_2.csv", index_col=0)

# Remove duplicates on Athlete in source0 and source2 to avoid row multiplication
source0_unique = source0.drop_duplicates(subset=['Athlete'])
source2_unique = source2.drop_duplicates(subset=['Athlete'])

# Join source1 with source0 on Athlete
join_1_0 = pd.merge(source1, source0_unique, on="Athlete", how="inner")

# Join the above result with source2 on Athlete
final_df = pd.merge(join_1_0, source2_unique, on="Athlete", how="inner")

# Select columns as per target schema
final_df = final_df[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country', 'Sport']]

# Cast columns to correct types
final_df['Age'] = final_df['Age'].astype(float)
final_df['Year'] = final_df['Year'].astype(int)
final_df['Gold Medals'] = final_df['Gold Medals'].astype(int)
final_df['Silver Medals'] = final_df['Silver Medals'].astype(int)
final_df['Bronze Medals'] = final_df['Bronze Medals'].astype(int)
final_df['Total Medals'] = final_df['Total Medals'].astype(int)
final_df['Closing Ceremony Date'] = final_df['Closing Ceremony Date'].astype(str)
final_df['Country'] = final_df['Country'].astype(str)
final_df['Sport'] = final_df['Sport'].astype(str)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_53/target_multisource_mcts.csv", index=False)