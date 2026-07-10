import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_38.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_39.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_40.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_41.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_42.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_43.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_44.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_45.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_46.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_47.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_48.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_49.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_50.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_51.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_52.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_53.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_54.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_55.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_56.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_57.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_58.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_59.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_filtered = df_all[df_all['type'] == 'Urban']

result = df_filtered.groupby('type', as_index=False)['driver_count'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)