import pandas as pd

# Thresholds
jaccard_threshold = 0.3
range_threshold = 0.2
pattern_threshold = 0.7

GLOBAL_SUMMARY = None  # store last table summary

# ----------------------------
# Column summary and table summary
# ----------------------------

class ColumnSummary:
    def __init__(self, col_name, dtype="str", unique_values=None):
        self.col_name = col_name
        self.dtype = dtype
        if unique_values is None:
            self.unique_values = []
        else:
            self.unique_values = unique_values
        self.col_name_score = 0

class TableSummary:
    def __init__(self, df):
        self.df = df
        self.cols = [ColumnSummary(c, str(df[c].dtype), df[c].unique()) for c in df.columns]

def get_table_summary(df, filename=None, param=None):
    return TableSummary(df)

# ----------------------------
# Column pair and table pair summary
# ----------------------------
class ColumnPair:
    def __init__(self, col_l, col_r):
        self.col_l = col_l
        self.col_r = col_r
        self.jaccard_value = 1.0
        self.range_overlap = 1.0
        self.pattern_value = 1.0

    def set_range_overlap(self):
        self.range_overlap = 1.0

    def set_pattern_value(self):
        self.pattern_value = 1.0

class TablePairSummary:
    def __init__(self, col_pairs):
        self.col_pairs = col_pairs

def get_table_pair_summary_for_category_value(df1, df2, summary1, summary2, flag=True):
    col_pairs = [ColumnPair(c1, c2) for c1, c2 in zip(summary1.cols, summary2.cols)]
    return TablePairSummary(col_pairs)

# ----------------------------
# Core function
# ----------------------------
def get_column_map(t1, t2, col_name=False):
    print("get column map")
    global GLOBAL_SUMMARY

    table1 = t1
    table2 = t2

    left_table_summary = get_table_summary(table1)
    if GLOBAL_SUMMARY is None:
        right_table_summary = get_table_summary(table2)
        GLOBAL_SUMMARY = right_table_summary
    else:
        right_table_summary = GLOBAL_SUMMARY

    table_pair = get_table_pair_summary_for_category_value(
        table1, table2, left_table_summary, right_table_summary, True
    )

    column_pair_map = {}
    for column_pair in table_pair.col_pairs:
        if column_pair.col_r not in column_pair_map:
            column_pair_map[column_pair.col_r] = [column_pair]
        else:
            column_pair_map[column_pair.col_r].append(column_pair)

    result = []
    for col, pairs in column_pair_map.items():
        keys = [(index, p.jaccard_value) for index, p in enumerate(pairs)]
        if col_name:
            keys = [(index, (p.jaccard_value + p.col_name_score)/2) for index, p in enumerate(pairs)]

        keys = [k for k in keys if k[1] > jaccard_threshold]
        if len(keys) > 0:
            sorted_keys = sorted(keys, key=lambda x: -x[1])
            pairs = [pairs[index] for index, v in sorted_keys]
            result.append(pairs)
        else:
            for pair in pairs:
                pair.set_range_overlap()
            keys = [(index, p.range_overlap) for index, p in enumerate(pairs)]
            if col_name:
                keys = [(index, (p.range_overlap + p.col_name_score)/2) for index, p in enumerate(pairs)]
            keys = [k for k in keys if k[1] > range_threshold]
            if len(keys) > 0:
                sorted_keys = sorted(keys, key=lambda x: -x[1])
                pairs = [pairs[index] for index, v in sorted_keys]
                result.append(pairs)
            else:
                for pair in pairs:
                    pair.set_pattern_value()
                keys = [(index, p.pattern_value) for index, p in enumerate(pairs)]
                if col_name:
                    keys = [(index, (p.pattern_value + p.col_name_score)/2) for index, p in enumerate(pairs)]
                sorted_keys = sorted(keys, key=lambda x: -x[1])
                pairs = [pairs[index] for index, v in sorted_keys]
                result.append(pairs)

    return result

