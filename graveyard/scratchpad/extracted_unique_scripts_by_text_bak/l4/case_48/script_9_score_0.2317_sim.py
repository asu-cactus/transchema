import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df = df0.copy()

df["WarID"] = df["WarNum"].astype("Int64")
df["Initiator"] = df["Initiator"].astype(str)

def to_int_nullable(series):
    return pd.to_numeric(series, errors='coerce').astype("Int64")

df["PolityID"] = to_int_nullable(df["CcodeA"])
df["PolityName"] = to_int_nullable(df["SideA"])

def choose_start_month(row):
    if pd.notna(row["StartMonth1"]):
        return row["StartMonth1"]
    elif pd.notna(row["StartMonth2"]):
        return row["StartMonth2"]
    else:
        return pd.NA

def choose_start_day(row):
    if pd.notna(row["StartDay1"]):
        return row["StartDay1"]
    elif pd.notna(row["StartDay2"]):
        return row["StartDay2"]
    else:
        return pd.NA

def choose_start_year(row):
    if pd.notna(row["StartYear1"]):
        return row["StartYear1"]
    elif pd.notna(row["StartYear2"]):
        return row["StartYear2"]
    else:
        return pd.NA

def choose_end_month(row):
    if pd.notna(row["EndMonth1"]):
        return row["EndMonth1"]
    elif pd.notna(row["EndMonth2"]):
        return row["EndMonth2"]
    else:
        return pd.NA

def choose_end_day(row):
    if pd.notna(row["EndDay1"]):
        return row["EndDay1"]
    elif pd.notna(row["EndDay2"]):
        return row["EndDay2"]
    else:
        return pd.NA

def choose_end_year(row):
    if pd.notna(row["EndYear1"]):
        return row["EndYear1"]
    elif pd.notna(row["EndYear2"]):
        return row["EndYear2"]
    else:
        return pd.NA

df["StartMonth"] = df.apply(choose_start_month, axis=1)
df["StartDay"] = df.apply(choose_start_day, axis=1)
df["StartYear"] = df.apply(choose_start_year, axis=1)
df["EndMonth"] = df.apply(choose_end_month, axis=1)
df["EndDay"] = df.apply(choose_end_day, axis=1)
df["EndYear"] = df.apply(choose_end_year, axis=1)

df["Outcome"] = to_int_nullable(df["Outcome"])

side_a_deaths = to_int_nullable(df["SideADeaths"])
side_b_deaths = to_int_nullable(df["SideBDeaths"])
df["Deaths"] = side_a_deaths.fillna(0) + side_b_deaths.fillna(0)
df["Deaths"] = df["Deaths"].astype("Int64")

result = df[[
    "Initiator",
    "WarID",
    "PolityID",
    "PolityName",
    "StartMonth",
    "StartDay",
    "StartYear",
    "EndMonth",
    "EndDay",
    "EndYear",
    "Outcome",
    "Deaths"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)