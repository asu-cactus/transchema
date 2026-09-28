import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length9_74/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length9_74/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length9_74/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

df_join = pd.merge(
    df0,
    df1,
    how="inner",
    left_on=["bid_id", "message_timestamp"],
    right_on=["sampled_bid_id", "message_timestamp"],
    suffixes=('_x', '_y')
)

df_join.to_csv(target_path, index=False)