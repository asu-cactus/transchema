import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_4.csv", index_col=0)

def rename_cols(df, suffix):
    return df.rename(columns={
        "Don't know/Refused/Missing": f"Don't know/Refused/Missing_{suffix}",
        "Normal Weight": f"Normal Weight_{suffix}",
        "Obese": f"Obese_{suffix}",
        "Overweight": f"Overweight_{suffix}",
        "Underweight": f"Underweight_{suffix}"
    })

df0r = rename_cols(df0, "0")
df1r = rename_cols(df1, "1")
df2r = rename_cols(df2, "2")
df3r = rename_cols(df3, "3")
df4r = rename_cols(df4, "4")

dfs = [df0r, df1r, df2r, df3r, df4r]

from functools import reduce

def multi_join(dfs):
    base = dfs[0]
    for df in dfs[1:]:
        base = base.merge(df, on=["Age Group", "Sex"], how="outer")
    return base

joined = multi_join(dfs)

age_map = {
    "Age 18 to 24": 5,
    "Age 25 to 34": 6,
    "Age 35 to 44": 7,
    "Age 45 to 54": 8,
    "Age 55 to 64": 9,
    "Age 65 to 74": 10,
    "Age 75+": 11,
    "Refused": 12
}

sex_map = {
    "Female": 5,
    "Male": 5,
    "Refused": 5
}

joined["Age Group"] = joined["Age Group"].map(age_map).astype("Int64")
joined["Sex"] = joined["Sex"].map(sex_map).astype("Int64")

def sum_cols(prefix):
    cols = [f"{col}_{prefix}" for col in ["Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]]
    return joined[cols].sum(axis=1, skipna=True)

joined["Don't know/Refused/Missing"] = sum_cols("0") + sum_cols("1") + sum_cols("2") + sum_cols("3") + sum_cols("4")
joined["Normal Weight"] = sum_cols("0") + sum_cols("1") + sum_cols("2") + sum_cols("3") + sum_cols("4")
joined["Obese"] = sum_cols("0") + sum_cols("1") + sum_cols("2") + sum_cols("3") + sum_cols("4")
joined["Overweight"] = sum_cols("0") + sum_cols("1") + sum_cols("2") + sum_cols("3") + sum_cols("4")
joined["Underweight"] = sum_cols("0") + sum_cols("1") + sum_cols("2") + sum_cols("3") + sum_cols("4")

# The above sums are repeated 5 times, fix by summing once over all suffixes:
joined["Don't know/Refused/Missing"] = joined[[f"Don't know/Refused/Missing_{i}" for i in range(5)]].sum(axis=1, skipna=True).astype("Int64")
joined["Normal Weight"] = joined[[f"Normal Weight_{i}" for i in range(5)]].sum(axis=1, skipna=True).astype("Int64")
joined["Obese"] = joined[[f"Obese_{i}" for i in range(5)]].sum(axis=1, skipna=True).astype("Int64")
joined["Overweight"] = joined[[f"Overweight_{i}" for i in range(5)]].sum(axis=1, skipna=True).astype("Int64")
joined["Underweight"] = joined[[f"Underweight_{i}" for i in range(5)]].sum(axis=1, skipna=True).astype("Int64")

joined = joined.reset_index(drop=True)
joined["index"] = joined.index.astype(int)

final_cols = ["index", "Age Group", "Sex", "Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]
result = joined[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_16/target_multisource_mcts.csv", index=False)