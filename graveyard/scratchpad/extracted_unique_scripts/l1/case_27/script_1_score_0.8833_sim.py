import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

agg_df = df0.groupby("day_week").agg({
    "ENTRIESn": "mean",
    "EXITSn": "mean",
    "ENTRIESn_hourly": "mean",
    "EXITSn_hourly": "mean",
    "hour": "mean",
    "weekday": "mean",
    "latitude": "mean",
    "longitude": "mean",
    "fog": "mean",
    "precipi": "mean",
    "pressurei": "mean",
    "rain": "mean",
    "tempi": "mean",
    "wspdi": "mean",
    "meanprecipi": "mean",
    "meanpressurei": "mean",
    "meantempi": "mean",
    "meanwspdi": "mean",
    "weather_lat": "mean",
    "weather_lon": "mean"
}).reset_index()

agg_df["day_week"] = agg_df["day_week"].astype(int)
agg_df["weekday"] = agg_df["weekday"].round().astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)