from hint_v2 import generate_transformation_hints
import hint_v1 as h
import summary
from model.aggregation.pwr import load_trained_model, predict_columns
from model.join.pwr import predict_join_columns
from sklearn.preprocessing import LabelEncoder
import hint_v3 as h3

def get_hints(prompt_type, hint_source,target_data_schema, file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, hint_flag, hints_truncate) :
    hints = []
    if(hint_source.startswith("v1")) : 
        if(prompt_type == "join") :
            hints = h.get_join_hints(hint_source,file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, hint_flag, hints_truncate)
        if(prompt_type == "group_by_aggregate") :
            hints = h.get_groupby_aggregate_hints(hint_source,file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, hint_flag, hints_truncate)
        if(prompt_type == "get_next_operator") :
            table_matching = h.get_table_matching(source_data_schema_list, source_data_name_list, target_data_schema)
            column_table_mapping = h.get_column_table_mapping(target_data_schema, source_data_schema_list, source_data_name_list)
            hints = [table_matching + "\n\n" + column_table_mapping]
    elif(hint_source == "v2") : 
        tables = summary.load_tables(directory + "/length" + len_idx_target_idx)
        # Load the models
        join_model = load_trained_model('model/join/join_model.json')
        key_model = load_trained_model('model/aggregation/key_model.json')

        # Predict join column pairs
        join_candidates = predict_join_columns(tables, join_model)
        candidate_matching_columns = [(f"{t1}.{c1}", f"{t2}.{c2}", s) for (t1, c1), (t2, c2), s in join_candidates]

        # Predict key columns for the target table
        target_table_name = 'target'
        target_df = tables[target_table_name]
        # Fit LabelEncoder on all possible data types
        all_data_types = ['int64', 'float64', 'object']  # Add more types if needed
        label_encoder = LabelEncoder()
        label_encoder.fit(all_data_types)
        # Predict key columns for all tables
        all_key_candidates = []
        key_candidates = predict_columns(tables, key_model, label_encoder)
        all_key_candidates.extend(key_candidates)

        # print(candidate_matching_columns,'\n\n',all_key_candidates)

        # Generate transformation hints
        source_dfs = [tables[table] for table in tables if table != target_table_name]
        hints = generate_transformation_hints(tables,source_dfs, target_df, mode='light', candidate_matching_columns=candidate_matching_columns, candidate_key_columns=key_candidates, type=prompt_type)
        # print(hints)

    elif(hint_source == "v3") :
        if(prompt_type == "join") :
            hints = h3.get_join_hints(hint_source,file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, hint_flag, hints_truncate)
        if(prompt_type == "group_by_aggregate") :
            hints = h3.get_groupby_aggregate_hints(hint_source,file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, hint_flag, hints_truncate)
        if(prompt_type == "union") : 
            hints = h3.get_union_hints(hint_source,file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, hint_flag, hints_truncate)
        if(prompt_type == "get_next_operator") :
            table_matching = h.get_table_matching(source_data_schema_list, source_data_name_list, target_data_schema)
            # column_table_mapping = h.get_column_table_mapping(target_data_schema, source_data_schema_list, source_data_name_list)
            hints = [table_matching]
        
        # return [hints]
    else : 
        pass
    return hints 