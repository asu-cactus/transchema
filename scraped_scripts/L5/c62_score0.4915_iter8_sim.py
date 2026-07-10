import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_4.csv", index_col=0)

joined_01 = pd.merge(df0, df1, on=["Sex", "Age Group"], suffixes=('_0', '_1'))

def combine_columns(row, col):
    v0 = row[f"{col}_0"]
    v1 = row[f"{col}_1"]
    if pd.isna(v0) and pd.isna(v1):
        return pd.NA
    if pd.isna(v0):
        return v1
    if pd.isna(v1):
        return v0
    return v0 + v1

cols_to_sum = ["Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]
for col in cols_to_sum:
    joined_01[col] = joined_01.apply(lambda r: combine_columns(r, col), axis=1)

joined_01 = joined_01[["Sex", "Age Group"] + cols_to_sum]

df_all = pd.concat([joined_01, df2, df3, df4], ignore_index=True)

df_all["Age Group"] = df_all["Age Group"].str.extract(r'(\d+)').astype(int)

df_all = df_all.groupby(["Sex", "Age Group"], as_index=False)[cols_to_sum].sum()

df_all = df_all.astype({
    "Sex": str,
    "Age Group": int,
    "Don't know/Refused/Missing": int,
    "Normal Weight": int,
    "Obese": int,
    "Overweight": int,
    "Underweight": int
})

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length5_62/target_multisource_mcts.csv", index=False)