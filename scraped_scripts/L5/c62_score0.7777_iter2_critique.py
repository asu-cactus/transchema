import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_62/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

# Fill NaN in numeric columns with 0 for sum aggregation
num_cols = ["Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]
df_all[num_cols] = df_all[num_cols].fillna(0)

agg_df = df_all.groupby('Sex').agg({
    'Age Group': pd.Series.nunique,
    "Don't know/Refused/Missing": 'sum',
    "Normal Weight": 'sum',
    "Obese": 'sum',
    "Overweight": 'sum',
    "Underweight": 'sum'
}).reset_index()

# Rename 'Age Group' aggregation column to match target schema
agg_df = agg_df.rename(columns={'Age Group': 'Age Group'})

# Convert types to match target schema
agg_df["Sex"] = agg_df["Sex"].astype(str)
agg_df["Age Group"] = agg_df["Age Group"].astype('Int64')
agg_df["Don't know/Refused/Missing"] = agg_df["Don't know/Refused/Missing"].astype('Int64')
agg_df["Normal Weight"] = agg_df["Normal Weight"].astype('Int64')
agg_df["Obese"] = agg_df["Obese"].astype('Int64')
agg_df["Overweight"] = agg_df["Overweight"].astype('Int64')
agg_df["Underweight"] = agg_df["Underweight"].astype('Int64')

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_62/target_multisource_mcts.csv", index=False)