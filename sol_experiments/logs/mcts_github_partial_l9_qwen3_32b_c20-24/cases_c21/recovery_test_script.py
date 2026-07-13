import pandas as pd

# Load all source tables
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_7.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_9.csv', index_col=0)
source10 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_21/test_10.csv', index_col=0)

# Join Source5 with all required dimension tables
df = pd.merge(source5, source0, on='Origen', how='left')
df = pd.merge(df, source1, on='Pronostico', how='left')
df = pd.merge(df, source2, on='Deteccion', how='left')
df = pd.merge(df, source3, on='TipoAhogamiento', how='left')
df = pd.merge(df, source4, on='Intervencion', how='left')
df = pd.merge(df, source6, on='Actividad', how='left')
df = pd.merge(df, source7, on='Causa', how='left')
df = pd.merge(df, source8, on='Reanimacion', how='left')
df = pd.merge(df, source9, on='Riesgo', how='left')
df = pd.merge(df, source10, on='Factor', how='left')

# Save to final destination
df.to_csv('autopipeline-benchmarks/github-pipelines/length9_21/target_multisource_mcts_recovery_test_val.csv')