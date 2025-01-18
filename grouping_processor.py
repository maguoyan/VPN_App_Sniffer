import os
import pandas as pd
from sklearn.model_selection import train_test_split


# 将csv文件中的数据根据时间戳分组
def csv_to_group(file_path, window_size=10.0, time_unit=0.1):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')

    # 计算时间窗口和时间单元的比例
    min_timestamp = df['timestamp'].iloc[0]

    # 将时间戳转换为对应的时间单元
    df['time_unit'] = ((df['timestamp'] - min_timestamp) / time_unit).round().astype(int)

    # 打印每个数据包的 timestamp 和 time_unit，确保计算正确
    print(f"min_timestamp: {min_timestamp}")
    print(f"Timestamp and calculated time_unit:")
    for i, row in df.iterrows():
        print(f"timestamp: {row['timestamp']}, time_unit: {row['time_unit']}")

    total_time_units = int((df['timestamp'].iloc[-1] - min_timestamp) / time_unit) + 1

    result = []
    group_number = 0
    # 按时间窗口切分
    for start_time_unit in range(0, total_time_units, int(window_size / time_unit)):
        end_time_unit = start_time_unit + int(window_size / time_unit) - 1  # 闭区间
        window_data = df[(df['time_unit'] >= start_time_unit) & (df['time_unit'] <= end_time_unit)]  # 使用闭区间

        print(f"Processing time window: ({start_time_unit}, {end_time_unit})")
        print(f"window_data time_units: {window_data['time_unit'].unique()}")  # 查看当前窗口内的所有唯一time_unit

        # 初始化一个时间窗口的特征向量
        window_feature_vector = []

        # 按时间单元计算特征
        for t_unit in range(start_time_unit, end_time_unit + 1):  # 包括end_time_unit
            time_unit_data = window_data[window_data['time_unit'] == t_unit]
            print(f"Processing time unit: {t_unit}, time_unit_data: {time_unit_data}")

            # 计算每个时间单元的特征值（包的长度和，考虑direction）
            time_unit_feature = time_unit_data.apply(
                lambda row: row['length'] if row['direction'] == 1 else -row['length'],
                axis=1
            ).sum()  # 对所有包长度求和

            window_feature_vector.append(time_unit_feature)

        # 将该时间窗口的特征添加到结果中
        result.append({
            'group_number': group_number,
            'time_window': (start_time_unit, end_time_unit),
            'feature_vector': window_feature_vector
        })
        group_number += 1
    return result




# 每组中两个特征向量的融合
def prepare_data_for_training(processed_data, label):
    X = []
    y = []
    for group in processed_data:
        feature_vector = group['feature_vector']
        X.append(feature_vector)  # 直接使用特征向量
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
'''
def test_csv_to_group():
    processed_data = csv_to_group('ike2_aiqiyi.csv', window_size=10.0, time_unit=0.1)

    for entry in processed_data:
        print(f"Feature Vector: {entry['feature_vector']}")

test_csv_to_group()
'''
# test grouping
# file_path = '../csv_data/test.csv'
# processed_data = csv_to_group(file_path)
# for entry in processed_data:
#     print(f"Time Window: {entry['time_window']}")
#     print(f"Feature Vector: {entry['feature_vector']}")
#     print()
