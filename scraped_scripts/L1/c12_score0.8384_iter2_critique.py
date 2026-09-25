import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_1.csv", index_col=0)

# LEFT join to keep all medal records
df = pd.merge(df0, df1, on="Athlete", how="left")

# Aggregate as per plan
agg_df = df.groupby(['Athlete', 'Year', 'Closing Ceremony Date', 'Country'], as_index=False).agg({
    'Age': 'mean',
    'Gold Medals': 'sum',
    'Silver Medals': 'sum',
    'Bronze Medals': 'sum',
    'Total Medals': 'sum'
})

# Ensure correct dtypes
agg_df["Age"] = agg_df["Age"].astype(float)
agg_df["Year"] = agg_df["Year"].astype(int)
agg_df["Gold Medals"] = agg_df["Gold Medals"].astype(int)
agg_df["Silver Medals"] = agg_df["Silver Medals"].astype(int)
agg_df["Bronze Medals"] = agg_df["Bronze Medals"].astype(int)
agg_df["Total Medals"] = agg_df["Total Medals"].astype(int)
agg_df["Closing Ceremony Date"] = agg_df["Closing Ceremony Date"].astype(str)
agg_df["Country"] = agg_df["Country"].astype(str)

# Reorder columns to target schema
agg_df = agg_df[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts.csv", index=False)