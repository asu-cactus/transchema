import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_27/test_0.csv', index_col=0)
grouped = df.groupby("day_week", as_index=False).agg({
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
    "weather_lon": "mean",
})

grouped["day_week"] = grouped["day_week"].round(1)  # Ensures correct float formatting
grouped["weekday"] = grouped["weekday"].round(2).astype(int)  # Converts to integer, based on original data

grouped.to_csv('autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts_recovery_test_val.csv', index=False)