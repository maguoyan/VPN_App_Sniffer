import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


# 将csv文件中的数据根据时间戳分组
def csv_to_group(file_path, time_interval=3.0):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')

    # 按时间间隔分组
    # 将时间戳除以时间间隔并向下取整，以此作为新的分组键
    min_timestamp = df['timestamp'].iloc[0]
    df['group'] = ((df['timestamp'] - min_timestamp) // time_interval).astype(int)
    grouped = df.groupby('group')

    result = []
    for group_name, group_data in grouped:
        # 分别提取 direction 为 1 和 -1 的数据
        direction_1 = group_data[group_data['direction'] == 1]
        direction_minus_1 = group_data[group_data['direction'] == -1]

        # 创建特征向量
        feature_vector_1 = direction_1['length'].tolist()
        feature_vector_minus_1 = direction_minus_1['length'].tolist()
        result.append({
            'group': group_name,
            'feature_vector_1': feature_vector_1,
            'feature_vector_minus_1': feature_vector_minus_1
        })

    return result


# 每组中两个特征向量的融合
def prepare_data_for_training(processed_data, label):
    X = []
    y = []
    for group in processed_data:
        feature_vector_1 = group['feature_vector_1']
        feature_vector_minus_1 = group['feature_vector_minus_1']
        combined_feature_vector = feature_vector_1 + feature_vector_minus_1
        X.append(combined_feature_vector)
        y.append(label)

    return X, y


# 填充变长的特征向量
def pad_feature_vectors(feature_vectors, max_length):
    padded_vectors = []
    for fv in feature_vectors:
        padding_length = max_length - len(fv)
        padded_vector = fv + [0] * padding_length
        padded_vectors.append(padded_vector)
    return padded_vectors


# 最后的数据处理，之后交给模型训练
def model_data_processor():
    all_X = []
    all_y = []

    # "ike2", "openvpn", "sstp"
    protocals = ["ike2"]
    for ptc in protocals:
        directory_path = "../csv_data/" + str(ptc)
        label = 0
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = directory_path + "/" + file

                processed_data = csv_to_group(file_path)
                X, y = prepare_data_for_training(processed_data, label)
                all_X.extend(X)
                all_y.extend(y)

                label += 1  # 每个文件对应一个应用，每个应用对应一个标签

    # 找到最长的特征向量长度
    max_feature_length = max(len(fv) for fv in all_X)
    # 填充所有特征向量（保证特征向量长度相同，这样才能满足sklearn的需求）
    all_X_padded = pad_feature_vectors(all_X, max_feature_length)

    X_train, X_test, y_train, y_test = train_test_split(all_X_padded, all_y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test


# test grouping
# file_path = '../csv_data/test.csv'
# processed_data = csv_to_group(file_path)
# for entry in processed_data:
#     print(f"Group: {entry['group']}")
#     print(f"Feature Vector (direction 1): {entry['feature_vector_1']}")
#     print(f"Feature Vector (direction -1): {entry['feature_vector_minus_1']}")
#     print()


