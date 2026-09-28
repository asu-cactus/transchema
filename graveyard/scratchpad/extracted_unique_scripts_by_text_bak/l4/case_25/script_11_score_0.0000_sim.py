import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv", index_col=0)

df0 = df0.rename(columns=lambda x: x + "_0")
df1 = df1.rename(columns=lambda x: x + "_1")
df2 = df2.rename(columns=lambda x: x + "_2")
df3 = df3.rename(columns=lambda x: x + "_3")

join_0 = pd.merge(df0, df1,
                  left_on=["country_code_0", "obs_type_0", "datetime_0", "station_0"],
                  right_on=["country_code_1", "obs_type_1", "datetime_1", "station_1"],
                  how="inner")

join_1 = pd.merge(join_0, df2,
                  left_on=["country_code_0", "obs_type_0", "datetime_0", "station_0"],
                  right_on=["country_code_2", "obs_type_2", "datetime_2", "station_2"],
                  how="inner")

join_2 = pd.merge(join_1, df3,
                  left_on=["country_code_0", "obs_type_0", "datetime_0", "station_0"],
                  right_on=["country_code_3", "obs_type_3", "datetime_3", "station_3"],
                  how="inner")

grouped = join_2.groupby(
    ["country_code_0", "station_0", "datetime_0", "obs_type_0"],
    as_index=False
).agg({
    "obs_value_0": "mean",
    "obs_value_1": "mean",
    "obs_value_2": "mean",
    "obs_value_3": "mean",
    "TMAX_F_0": "mean",
    "TMAX_F_1": "mean",
    "TMAX_F_2": "mean",
    "TMAX_F_3": "mean",
    "month_0": "mean",
    "month_1": "mean",
    "month_2": "mean",
    "month_3": "mean"
})

grouped["obs_value"] = grouped[["obs_value_0", "obs_value_1", "obs_value_2", "obs_value_3"]].mean(axis=1).round().astype(int)
grouped["TMAX_F"] = grouped[["TMAX_F_0", "TMAX_F_1", "TMAX_F_2", "TMAX_F_3"]].mean(axis=1).round().astype(int)
grouped["month"] = grouped[["month_0", "month_1", "month_2", "month_3"]].mean(axis=1).round().astype(int)

def convert_station(x):
    if isinstance(x, str):
        digits = ''.join(filter(str.isdigit, x))
        return int(digits) if digits else 0
    elif pd.isna(x):
        return 0
    else:
        return int(x)

grouped["station"] = grouped["station_0"].apply(convert_station)
grouped["datetime"] = pd.to_datetime(grouped["datetime_0"], errors='coerce').dt.strftime('%Y%m%d').astype(float).fillna(0).astype(int)
grouped["obs_type"] = grouped["obs_type_0"].astype('category').cat.codes.astype(int)
grouped["country_code"] = grouped["country_code_0"].astype(str)

result = grouped[["country_code", "station", "datetime", "obs_type", "obs_value", "TMAX_F", "month"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)