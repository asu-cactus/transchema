import json


def get_test_cases_ids(json_file_path, len_id, max_len_id, target_id, max_target_id):
    # Read the JSON file
    print(json_file_path)
    with open(json_file_path, 'r') as file:
        data_list = json.load(file)

    # Find the item with the specified Source Data Name
    ids = [item["Target Data Name"] for item in data_list]

    # Adjust the filter criteria
    filtered_ids = []
    for id in ids:
        parts = id[6:].split('_')
        if len(parts) >= 2:
            len_part = int(parts[0])
            target_part = int(parts[1])
            if len_id <= len_part <= max_len_id and target_id <= target_part <= max_target_id:
                filtered_ids.append(id)

    # bad_ids = ['Target1_16']
    past_at_least_once = ['Target1_0', 'Target1_3', 'Target1_4', 'Target1_6', 'Target1_11', 'Target1_20',
                          'Target1_21', 'Target1_29', 'Target1_34', 'Target1_35', 'Target1_38',
                          'Target1_55', 'Target1_60', 'Target1_65', 'Target1_67', 'Target1_71',
                          'Target1_72', 'Target1_80', 'Target1_84']
    finish_issue = ['Target1_27', 'Target1_46', 'Target1_97']  # 27, 46, 97
    further_finish_issue = ['Target1_97']
    with_dirty_rows = ['Target1_40', 'Target1_59']
    with_similarity_issue = ['Target1_10']  # , 'Target1_23', 'Target1_62', 'Target1_86', 'Target1_97']
    with_syntax_issue = ['Target1_44', 'Target1_78', 'Target1_88', 'Target1_89', 'Target1_90', 'Target1_91',
                         'Target1_92', 'Target1_93']

    print('Total number of test cases:', len(filtered_ids))
    # print('Number of bad test cases:', len(bad_ids))
    # filtered_ids = [id for id in filtered_ids if id not in bad_ids]
    # filtered_ids = [id for id in filtered_ids if id not in past_at_least_once]
    baseline_5_iters = [
        "Target1_6", "Target1_9", "Target1_13", "Target1_16", "Target1_18", "Target1_22",
        "Target1_23", "Target1_24", "Target1_27", "Target1_34", "Target1_35", "Target1_38",
        "Target1_40", "Target1_41", "Target1_43", "Target1_44", "Target1_46", "Target1_52",
        "Target1_54", "Target1_55", "Target1_57", "Target1_68", "Target1_72", "Target1_75",
        "Target1_78", "Target1_80", "Target1_81", "Target1_84", "Target1_86", "Target1_87",
        "Target1_88", "Target1_89", "Target1_90", "Target1_91", "Target1_93", "Target1_95",
        "Target1_97", "Target1_99"
    ]
    baseline_5_iters_2nd = [
        'Target1_6', 'Target1_35', 'Target1_40', 'Target1_57', 'Target1_72', 'Target1_84',
        'Target1_88', 'Target1_91', 'Target1_93']
    baseline_5_iters_3rd = [
        'Target1_72', 'Target1_84', 'Target1_91', 'Target1_93']
    baseline_5_iters_4th = ['Target1_55', 'Target1_72', 'Target1_88']
    join_1 = ['Target1_1',   'Target1_2', 'Target1_5',
               'Target1_7', 'Target1_8',   'Target1_12',
               'Target1_14', 'Target1_15',
               'Target1_17',  'Target1_19', 'Target1_25',
               'Target1_26', 'Target1_28', 'Target1_30', 'Target1_31',
               'Target1_32', 'Target1_33', 'Target1_36',
               'Target1_37', 'Target1_39',  'Target1_42',
               'Target1_45',  'Target1_47',  'Target1_49',
               'Target1_50',  'Target1_51', 'Target1_56',  'Target1_58',
                 'Target1_63', 'Target1_64',
               'Target1_66', 'Target1_69',  'Target1_70', 'Target1_73',
               'Target1_74',  'Target1_76', 'Target1_79',
               'Target1_83', 'Target1_85',
              'Target1_94',  'Target1_96', 'Target1_98']
    join_1_failed = ['Target1_8','Target1_37','Target1_39','Target1_58','Target1_64','Target1_69','Target1_74','Target1_79',
                     'Target1_85','Target1_96','Target1_98',]
    j1sf =['Target1_37','Target1_98']
    join_2 = ['Target2_0', 'Target2_2', 'Target2_3', 'Target2_4', 'Target2_5',
              'Target2_6', 'Target2_7', 'Target2_8', 'Target2_9', 'Target2_10',
              'Target2_11', 'Target2_12', 'Target2_13', 'Target2_14', 'Target2_15',
              'Target2_16', 'Target2_17', 'Target2_18', 'Target2_20', 'Target2_21',
              'Target2_22', 'Target2_23', 'Target2_24', 'Target2_25', 'Target2_26',
              'Target2_27', 'Target2_28', 'Target2_29', 'Target2_30', 'Target2_31',
              'Target2_32', 'Target2_33', 'Target2_34', 'Target2_35', 'Target2_36',
              'Target2_37', 'Target2_38', 'Target2_39', 'Target2_40', 'Target2_41',
              'Target2_42', 'Target2_43', 'Target2_44', 'Target2_46', 'Target2_47',
              'Target2_48', 'Target2_49', 'Target2_50', 'Target2_51', 'Target2_52',
              'Target2_53', 'Target2_54', 'Target2_55', 'Target2_56', 'Target2_57',
              'Target2_58', 'Target2_59', 'Target2_60', 'Target2_62', 'Target2_63',
              'Target2_64', 'Target2_65', 'Target2_66', 'Target2_67', 'Target2_68',
              'Target2_69', 'Target2_70', 'Target2_71', 'Target2_72', 'Target2_73',
              'Target2_74', 'Target2_75', 'Target2_76', 'Target2_77', 'Target2_78',
              'Target2_79', 'Target2_81', 'Target2_82', 'Target2_84', 'Target2_85',
              'Target2_86', 'Target2_88', 'Target2_89', 'Target2_91', 'Target2_92',
              'Target2_93', 'Target2_95', 'Target2_96', 'Target2_97', 'Target2_98',
              'Target2_99']
    join_2_failed = ['Target2_2', 'Target2_3', 'Target2_5', 'Target2_6', 'Target2_7', 'Target2_8', 'Target2_9',
                     'Target2_10', 'Target2_11', 'Target2_12', 'Target2_13', 'Target2_14', 'Target2_15', 'Target2_16',
                      'Target2_18', 'Target2_20', 'Target2_22', 'Target2_23', 'Target2_25',
                     'Target2_27', 'Target2_28', 'Target2_29', 'Target2_31', 'Target2_32', 'Target2_33', 'Target2_34',
                     'Target2_35',  'Target2_37', 'Target2_39', 'Target2_41', 'Target2_42', 'Target2_43',
                     'Target2_44', 'Target2_47', 'Target2_48', 'Target2_49', 'Target2_51', 'Target2_52', 'Target2_53',
                     'Target2_54', 'Target2_58', 'Target2_59', 'Target2_60', 'Target2_62', 'Target2_63', 'Target2_64',
                     'Target2_65', 'Target2_67', 'Target2_69', 'Target2_73', 'Target2_74', 'Target2_75', 'Target2_76',
                     'Target2_77', 'Target2_81', 'Target2_82', 'Target2_84', 'Target2_85', 'Target2_86', 'Target2_88',
                     'Target2_91', 'Target2_92', 'Target2_93', 'Target2_95', 'Target2_96', 'Target2_99']
    join_3 = ['Target3_1', 'Target3_2', 'Target3_3', 'Target3_5', 'Target3_6', 'Target3_7',
              'Target3_8', 'Target3_9', 'Target3_10', 'Target3_14', 'Target3_15', 'Target3_16',
              'Target3_17', 'Target3_18', 'Target3_19', 'Target3_22', 'Target3_23', 'Target3_24',
              'Target3_25', 'Target3_26', 'Target3_27', 'Target3_28', 'Target3_29', 'Target3_30',
              'Target3_31', 'Target3_32', 'Target3_33', 'Target3_34', 'Target3_35', 'Target3_36',
              'Target3_37', 'Target3_38', 'Target3_39', 'Target3_40', 'Target3_41', 'Target3_42',
              'Target3_43', 'Target3_44', 'Target3_45', 'Target3_46', 'Target3_47', 'Target3_48',
              'Target3_50', 'Target3_51', 'Target3_52', 'Target3_53', 'Target3_54', 'Target3_55',
              'Target3_56', 'Target3_57', 'Target3_58', 'Target3_59', 'Target3_60', 'Target3_61',
              'Target3_62', 'Target3_63', 'Target3_65', 'Target3_66', 'Target3_67', 'Target3_68',
              'Target3_69', 'Target3_70', 'Target3_71', 'Target3_72', 'Target3_73', 'Target3_74',
              'Target3_75', 'Target3_76', 'Target3_77', 'Target3_78', 'Target3_79', 'Target3_80',
              'Target3_81', 'Target3_82', 'Target3_83', 'Target3_84', 'Target3_85', 'Target3_86',
              'Target3_87', 'Target3_88', 'Target3_91', 'Target3_92', 'Target3_93', 'Target3_94',
              'Target3_95', 'Target3_96', 'Target3_97', 'Target3_98', 'Target3_99']
    join_3_failed = ['Target3_1', 'Target3_2', 'Target3_3', 'Target3_5', 'Target3_7', 'Target3_8', 'Target3_9',
                     'Target3_14', 'Target3_18', 'Target3_19', 'Target3_22', 'Target3_23', 'Target3_25', 'Target3_26',
                     'Target3_27', 'Target3_32', 'Target3_33', 'Target3_34', 'Target3_35', 'Target3_36', 'Target3_37',
                     'Target3_38', 'Target3_43', 'Target3_47', 'Target3_52', 'Target3_53', 'Target3_57', 'Target3_58',
                     'Target3_61', 'Target3_62', 'Target3_63', 'Target3_65', 'Target3_66', 'Target3_67', 'Target3_68',
                     'Target3_71', 'Target3_75', 'Target3_79', 'Target3_80', 'Target3_81', 'Target3_82', 'Target3_83',
                     'Target3_84', 'Target3_85', 'Target3_86', 'Target3_87', 'Target3_88', 'Target3_91', 'Target3_92',
                     'Target3_93', 'Target3_95',  'Target3_97', 'Target3_98', 'Target3_99']

    join_4 = ['Target4_1', 'Target4_2', 'Target4_3', 'Target4_4', 'Target4_5', 'Target4_6',
              'Target4_7', 'Target4_8', 'Target4_9', 'Target4_10', 'Target4_11', 'Target4_12', 'Target4_13',
              'Target4_14', 'Target4_15', 'Target4_16', 'Target4_17', 'Target4_23', 'Target4_24', 'Target4_25',
              'Target4_26', 'Target4_27', 'Target4_28', 'Target4_29', 'Target4_30', 'Target4_31', 'Target4_32',
              'Target4_33', 'Target4_34', 'Target4_35', 'Target4_36', 'Target4_37', 'Target4_38', 'Target4_39',
              'Target4_40', 'Target4_41', 'Target4_42', 'Target4_43', 'Target4_44', 'Target4_45', 'Target4_46',
              'Target4_47', 'Target4_51', 'Target4_52', 'Target4_53', 'Target4_54', 'Target4_55', 'Target4_56',
              'Target4_57', 'Target4_58', 'Target4_59', 'Target4_60', 'Target4_61', 'Target4_62', 'Target4_63',
              'Target4_64', 'Target4_65', 'Target4_66', 'Target4_68', 'Target4_69', 'Target4_70', 'Target4_72',
              'Target4_73', 'Target4_75', 'Target4_76', 'Target4_77', 'Target4_78', 'Target4_79', 'Target4_80',
              'Target4_81', 'Target4_82', 'Target4_83', 'Target4_84', 'Target4_86', 'Target4_87', 'Target4_88',
              'Target4_89', 'Target4_90', 'Target4_91', 'Target4_92', 'Target4_93', 'Target4_94', 'Target4_95',
              'Target4_96']
    join_4_failed = [
                     'Target4_1',  'Target4_3', 'Target4_4', 'Target4_5', 'Target4_6', 'Target4_7', 'Target4_8',
                     'Target4_9', 'Target4_10', 'Target4_11', 'Target4_12', 'Target4_13', 'Target4_14', 'Target4_15', 'Target4_16',
                     'Target4_17', 'Target4_23', 'Target4_24', 'Target4_25', 'Target4_26', 'Target4_27', 'Target4_28', 'Target4_29',
                     'Target4_30', 'Target4_31', 'Target4_32', 'Target4_33', 'Target4_34', 'Target4_35', 'Target4_36', 'Target4_37',
                     'Target4_38', 'Target4_39', 'Target4_40', 'Target4_41', 'Target4_42', 'Target4_43', 'Target4_44', 'Target4_45',
                     'Target4_46', 'Target4_47', 'Target4_51', 'Target4_52', 'Target4_53', 'Target4_54', 'Target4_55', 'Target4_56',
                     'Target4_57', 'Target4_58', 'Target4_59', 'Target4_60', 'Target4_61', 'Target4_62', 'Target4_63', 'Target4_64',
                     'Target4_65', 'Target4_68', 'Target4_70', 'Target4_72', 'Target4_73', 'Target4_75', 'Target4_76', 'Target4_77',
                     'Target4_78', 'Target4_80', 'Target4_81', 'Target4_82', 'Target4_84', 'Target4_86', 'Target4_87', 'Target4_89',
                     'Target4_90', 'Target4_91', 'Target4_92', 'Target4_93', 'Target4_94', 'Target4_95', 'Target4_96']
    join_5 = ['Target5_0', 'Target5_1', 'Target5_2', 'Target5_3', 'Target5_4', 'Target5_5', 'Target5_6', 'Target5_7',
              'Target5_8', 'Target5_9', 'Target5_10', 'Target5_11', 'Target5_12', 'Target5_13', 'Target5_14', 'Target5_15',
              'Target5_16', 'Target5_17', 'Target5_18', 'Target5_19', 'Target5_20', 'Target5_21', 'Target5_22', 'Target5_23',
              'Target5_24', 'Target5_25', 'Target5_26', 'Target5_27', 'Target5_28', 'Target5_29', 'Target5_30', 'Target5_31',
              'Target5_32', 'Target5_33', 'Target5_34', 'Target5_35', 'Target5_37', 'Target5_38', 'Target5_39', 'Target5_40',
              'Target5_41', 'Target5_42', 'Target5_43', 'Target5_44', 'Target5_46', 'Target5_47', 'Target5_48', 'Target5_49',
              'Target5_50', 'Target5_51', 'Target5_52', 'Target5_55', 'Target5_56', 'Target5_57', 'Target5_58', 'Target5_61',
              'Target5_62', 'Target5_63', 'Target5_64', 'Target5_65', 'Target5_66', 'Target5_67', 'Target5_68', 'Target5_69',
              'Target5_70', 'Target5_71', 'Target5_72', 'Target5_73', 'Target5_74', 'Target5_75', 'Target5_76', 'Target5_77',
              'Target5_78', 'Target5_79', 'Target5_81', 'Target5_83', 'Target5_85', 'Target5_86', 'Target5_87', 'Target5_88',
              'Target5_89', 'Target5_90', 'Target5_91', 'Target5_93', 'Target5_94', 'Target5_95', 'Target5_96', 'Target5_97']
    join_5_failed = [   'Target5_3',
                     'Target5_4', 'Target5_6', 'Target5_7', 'Target5_8', 'Target5_9', 'Target5_11', 'Target5_12',
                     'Target5_13', 'Target5_14', 'Target5_15', 'Target5_16', 'Target5_17', 'Target5_18', 'Target5_19',
                     'Target5_20', 'Target5_21', 'Target5_23', 'Target5_24', 'Target5_25', 'Target5_26', 'Target5_27',
                     'Target5_28', 'Target5_30', 'Target5_31', 'Target5_33', 'Target5_34', 'Target5_35', 'Target5_37',
                     'Target5_38', 'Target5_39', 'Target5_40', 'Target5_41', 'Target5_42', 'Target5_43', 'Target5_44',
                     'Target5_46', 'Target5_47', 'Target5_48', 'Target5_49', 'Target5_50', 'Target5_51', 'Target5_52',
                     'Target5_55', 'Target5_56', 'Target5_57', 'Target5_58', 'Target5_61', 'Target5_62', 'Target5_63',
                     'Target5_64', 'Target5_65', 'Target5_66', 'Target5_67', 'Target5_69', 'Target5_70', 'Target5_71',
                     'Target5_72', 'Target5_73', 'Target5_74', 'Target5_75', 'Target5_77', 'Target5_78', 'Target5_79',
                     'Target5_81', 'Target5_83', 'Target5_85', 'Target5_86', 'Target5_87', 'Target5_88', 'Target5_89',
                     'Target5_90', 'Target5_91', 'Target5_93', 'Target5_94', 'Target5_96', 'Target5_97']

    join_6 = ['Target6_0', 'Target6_3', 'Target6_5', 'Target6_6', 'Target6_7', 'Target6_8', 'Target6_9', 'Target6_10',
              'Target6_11', 'Target6_12', 'Target6_13', 'Target6_15', 'Target6_16', 'Target6_17', 'Target6_18', 'Target6_19',
              'Target6_20', 'Target6_21', 'Target6_22', 'Target6_23', 'Target6_24', 'Target6_25', 'Target6_26', 'Target6_27',
              'Target6_28', 'Target6_29', 'Target6_30', 'Target6_31', 'Target6_32', 'Target6_33', 'Target6_34', 'Target6_35',
              'Target6_36', 'Target6_37', 'Target6_38', 'Target6_39', 'Target6_40', 'Target6_41', 'Target6_42', 'Target6_43',
              'Target6_44', 'Target6_45', 'Target6_46', 'Target6_47', 'Target6_48', 'Target6_49', 'Target6_50', 'Target6_51',
              'Target6_52', 'Target6_53', 'Target6_54', 'Target6_55', 'Target6_56', 'Target6_57', 'Target6_58', 'Target6_59',
              'Target6_60', 'Target6_61', 'Target6_62', 'Target6_63', 'Target6_64', 'Target6_65', 'Target6_66', 'Target6_67',
              'Target6_68', 'Target6_69', 'Target6_70', 'Target6_71', 'Target6_72', 'Target6_73', 'Target6_74', 'Target6_75',
              'Target6_76', 'Target6_77', 'Target6_78', 'Target6_79', 'Target6_80', 'Target6_81', 'Target6_82', 'Target6_83',
              'Target6_84', 'Target6_85', 'Target6_86', 'Target6_87', 'Target6_88', 'Target6_89', 'Target6_90', 'Target6_92',
              'Target6_93', 'Target6_94', 'Target6_95', 'Target6_96', 'Target6_97', 'Target6_98', 'Target6_99']
    join_6_failed =[ 'Target6_0', 'Target6_3', 'Target6_6', 'Target6_7',
                    'Target6_8', 'Target6_9', 'Target6_10', 'Target6_12', 'Target6_13', 'Target6_15', 'Target6_16',
                    'Target6_17', 'Target6_18', 'Target6_19', 'Target6_20', 'Target6_21', 'Target6_22', 'Target6_23',
                    'Target6_24', 'Target6_25', 'Target6_26', 'Target6_27', 'Target6_28', 'Target6_29', 'Target6_31',
                    'Target6_33', 'Target6_34', 'Target6_35', 'Target6_36', 'Target6_37', 'Target6_38', 'Target6_39',
                    'Target6_40', 'Target6_41', 'Target6_42', 'Target6_43', 'Target6_44', 'Target6_46', 'Target6_49',
                    'Target6_50', 'Target6_51', 'Target6_52', 'Target6_53', 'Target6_54', 'Target6_55', 'Target6_56',
                    'Target6_57', 'Target6_58', 'Target6_59', 'Target6_61', 'Target6_62', 'Target6_64', 'Target6_65',
                    'Target6_69', 'Target6_70', 'Target6_71', 'Target6_72', 'Target6_73', 'Target6_74', 'Target6_75',
                    'Target6_76', 'Target6_77', 'Target6_78', 'Target6_79', 'Target6_80', 'Target6_81', 'Target6_83',
                    'Target6_85', 'Target6_86', 'Target6_87', 'Target6_88', 'Target6_90', 'Target6_92', 'Target6_93',
                    'Target6_94', 'Target6_95', 'Target6_96', 'Target6_97', 'Target6_98']

    join_9 = [ 'Target9_1', 'Target9_2', 'Target9_3', 'Target9_4', 'Target9_5', 'Target9_6', 'Target9_7',
              'Target9_8', 'Target9_9', 'Target9_10', 'Target9_11', 'Target9_12', 'Target9_13', 'Target9_14', 'Target9_15',
              'Target9_16', 'Target9_17', 'Target9_18', 'Target9_19', 'Target9_20', 'Target9_21', 'Target9_22', 'Target9_23',
              'Target9_24', 'Target9_25', 'Target9_26', 'Target9_27', 'Target9_28', 'Target9_29', 'Target9_30', 'Target9_31',
              'Target9_32', 'Target9_33', 'Target9_34', 'Target9_35', 'Target9_36', 'Target9_37', 'Target9_38', 'Target9_39',
              'Target9_40', 'Target9_41', 'Target9_42', 'Target9_43', 'Target9_44', 'Target9_45', 'Target9_46', 'Target9_47',
              'Target9_48', 'Target9_49', 'Target9_50', 'Target9_51', 'Target9_52', 'Target9_53', 'Target9_54', 'Target9_55',
              'Target9_56', 'Target9_57', 'Target9_58', 'Target9_59', 'Target9_60', 'Target9_61', 'Target9_62', 'Target9_63',
              'Target9_64', 'Target9_65', 'Target9_66', 'Target9_67', 'Target9_68', 'Target9_69', 'Target9_70', 'Target9_71',
              'Target9_72', 'Target9_73', 'Target9_74', 'Target9_75', 'Target9_76', 'Target9_77', 'Target9_78', 'Target9_79',
              'Target9_80', 'Target9_81', 'Target9_82', 'Target9_83', 'Target9_84', 'Target9_85', 'Target9_86', 'Target9_87',
              'Target9_88', 'Target9_89', 'Target9_90', 'Target9_91', 'Target9_92', 'Target9_93', 'Target9_94', 'Target9_95',
              'Target9_96', 'Target9_97', 'Target9_98', 'Target9_99']
    join_9_failed = ['Target9_0', 'Target9_1', 'Target9_2', 'Target9_3', 'Target9_4', 'Target9_6', 'Target9_11',
                     'Target9_12', 'Target9_13', 'Target9_14', 'Target9_15', 'Target9_16', 'Target9_17', 'Target9_18',
                     'Target9_19', 'Target9_20', 'Target9_21', 'Target9_22', 'Target9_23', 'Target9_24', 'Target9_25',
                     'Target9_26', 'Target9_27', 'Target9_28', 'Target9_29', 'Target9_30', 'Target9_31', 'Target9_32',
                     'Target9_33', 'Target9_34', 'Target9_35', 'Target9_36', 'Target9_37', 'Target9_38', 'Target9_39',
                     'Target9_40', 'Target9_41', 'Target9_42', 'Target9_43', 'Target9_44', 'Target9_45', 'Target9_46',
                     'Target9_47', 'Target9_48', 'Target9_49', 'Target9_50', 'Target9_51', 'Target9_52', 'Target9_53',
                     'Target9_54', 'Target9_55', 'Target9_56', 'Target9_57', 'Target9_58', 'Target9_59', 'Target9_61',
                     'Target9_62', 'Target9_67', 'Target9_68', 'Target9_69', 'Target9_70', 'Target9_71', 'Target9_72',
                     'Target9_73', 'Target9_74', 'Target9_75', 'Target9_76', 'Target9_77', 'Target9_78', 'Target9_79',
                     'Target9_80', 'Target9_82', 'Target9_83', 'Target9_87', 'Target9_88', 'Target9_96', 'Target9_97']

    non_join = ['Target2_1', 'Target2_19', 'Target2_45', 'Target2_61', 'Target2_80',
                'Target2_83', 'Target2_87', 'Target2_90', 'Target2_94', 'Target3_0',
                'Target3_4', 'Target3_11', 'Target3_12', 'Target3_13', 'Target3_20',
                'Target3_21', 'Target3_49', 'Target3_64', 'Target3_89', 'Target3_90',
                'Target4_18', 'Target4_19', 'Target4_20', 'Target4_21', 'Target4_22',
                'Target4_48', 'Target4_49', 'Target4_50', 'Target4_67', 'Target4_71',
                'Target4_74', 'Target4_85', 'Target4_97', 'Target4_98', 'Target4_99',
                'Target5_36', 'Target5_45', 'Target5_53', 'Target5_54', 'Target5_59',
                'Target5_60', 'Target5_80', 'Target5_82', 'Target5_84', 'Target5_92',
                'Target6_1', 'Target6_2', 'Target6_4', 'Target6_14', 'Target6_91']
    join_test = [
                 'Target3_34', 'Target3_35', 'Target3_36',
              'Target3_37', 'Target3_38', 'Target3_39', 'Target3_40', 'Target3_41', 'Target3_42',
              'Target3_43', 'Target3_44', 'Target3_45', 'Target3_46', 'Target3_47', 'Target3_48',
              'Target3_50', 'Target3_51', 'Target3_52', 'Target3_53', 'Target3_54', 'Target3_55',
              'Target3_56', 'Target3_57', 'Target3_58', 'Target3_59', 'Target3_60', 'Target3_61',
              'Target3_62', 'Target3_63', 'Target3_65', 'Target3_66', 'Target3_67', 'Target3_68',
              'Target3_69', 'Target3_70', 'Target3_71', 'Target3_72', 'Target3_73', 'Target3_74',
              'Target3_75', 'Target3_76', 'Target3_77', 'Target3_78', 'Target3_79', 'Target3_80',
              'Target3_81', 'Target3_82', 'Target3_83', 'Target3_84', 'Target3_85', 'Target3_86',
              'Target3_87', 'Target3_88', 'Target3_91', 'Target3_92', 'Target3_93', 'Target3_94',
              'Target3_95', 'Target3_96', 'Target3_97', 'Target3_98', 'Target3_99']
    cot_1 = ['Target1_0', 'Target1_3', 'Target1_4', 'Target1_6', 'Target1_10', 'Target1_11', 'Target1_13',
             'Target1_20', 'Target1_21', 'Target1_29', 'Target1_38', 'Target1_46', 'Target1_48',
             'Target1_57', 'Target1_59', 'Target1_60', 'Target1_61', 'Target1_65', 'Target1_67',
             'Target1_71', 'Target1_80'
             ]

    seen = set()
    filtered_ids = [x for x in filtered_ids if not (x in seen or seen.add(x))]
    print(len(filtered_ids))

    return ['Target5_39']

