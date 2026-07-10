import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

r0 = pd.merge(s0, s1, on="Artist", how="outer")
r1 = pd.merge(r0, s2, on="Artist", how="outer")
r2 = pd.merge(r1, s3, on="Artist", how="outer")
r3 = pd.merge(r2, s4, on="Artist", how="outer")
r4 = pd.merge(r3, s5, on="Artist", how="outer")
r5 = pd.merge(r4, s6, on="Artist", how="outer")
r6 = pd.merge(r5, s7, on="Artist", how="outer")
r7 = pd.merge(r6, s8, on="Artist", how="outer")

r7["Year Inducted"] = pd.to_numeric(r7["Year Inducted"], errors='coerce')
r7["Years Waited"] = pd.to_numeric(r7["Years Waited"], errors='coerce').astype('Int64')
r7["# of Years Nominated"] = pd.to_numeric(r7["# of Years Nominated"], errors='coerce').astype('Int64')
r7["Influenced"] = pd.to_numeric(r7["Influenced"], errors='coerce').astype('Int64')
r7["Albums in RS500"] = pd.to_numeric(r7["Albums in RS500"], errors='coerce').astype('Int64')
r7["Top 100 Singles"] = pd.to_numeric(r7["Top 100 Singles"], errors='coerce').astype('Int64')
r7["Highest Position"] = pd.to_numeric(r7["Highest Position"], errors='coerce').astype('Int64')
r7["Times on Cover of RS"] = pd.to_numeric(r7["Times on Cover of RS"], errors='coerce').astype('Int64')
r7["Certified Units (Millions)"] = pd.to_numeric(r7["Certified Units (Millions)"], errors='coerce')
r7["Score"] = pd.to_numeric(r7["Score"], errors='coerce')
r7["Spotify"] = pd.to_numeric(r7["Spotify"], errors='coerce').astype('Int64')

final_cols = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
              'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position',
              'Times on Cover of RS', 'Score', 'Spotify']

result = r7[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)