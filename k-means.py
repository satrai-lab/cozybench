import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix


# def preprocess_data():
#     # 读取数据
#     df = pd.read_csv('./knn/ashrae_comfort_data.csv', low_memory=False)
#
#     # 计算 BMI 并添加到 DataFrame 中
#     df['BMI'] = df['wt'] / ((df['ht']) ** 2)
#
#     # 选择特征，包括 BMI 而不是 ht 和 wt
#     features = ['season', 'age', 'gender', 'ta', 'thermal_sensation', 'BMI']
#
#     df['season'] = df['season'].map({'winter': 0, 'summer': 1})
#
#     # 去除缺失值数量大于 2 的行
#     df = df[df[features].isnull().sum(axis=1) <= 1]
#
#     print("缺失值情况:")
#     print(df[features].isna().sum())
#
#     imputer = KNNImputer(n_neighbors=5)
#     df[features] = imputer.fit_transform(df[features])
#
#     # 查看填补缺失值后的情况
#     print("填补缺失值后的情况:")
#     print(df[features].isna().sum())
#
#     df[features].to_csv('./knn/KNN_processed_ashrae_comfort_data.csv', index=False)
#
#
# # preprocess_data()
#
# # 读取处理过的数据集
# df = pd.read_csv('knn/KNN_processed_ashrae_comfort_data.csv')
#
# # 确保列名一致
# features = ['season', 'age', 'gender', 'ta', 'thermal_sensation', 'BMI']
#
# X = df[features]
#
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)
#
# # 使用肘部法则确定最佳K值
# # inertia = []
# # for k in range(1, 11):
# #     kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
# #     kmeans.fit(X_scaled)
# #     inertia.append(kmeans.inertia_)
# #
# # plt.plot(range(1, 11), inertia, marker='o')
# # plt.xlabel('Number of clusters')
# # plt.ylabel('Inertia')
# # plt.title('Elbow Method for Optimal k')
# # plt.show()
#
#
# optimal_k = 5  # 根据肘部法则选择最佳K值
# kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
# df['cluster'] = kmeans.fit_predict(X_scaled)
#
# # 检查聚类结果
# print(df['cluster'].value_counts())
#
# # 保存聚类结果
# df.to_csv('clustered_ashrae_comfort_data.csv', index=False)
#
# # 计算每个聚类组中不同 ta 值对应的 thermal_sensation 平均值
# avg_thermal_sensation = df.groupby(['cluster', 'ta'])['thermal_sensation'].mean().reset_index()
#
# # 绘制图表
# plt.figure(figsize=(10, 6))
# for cluster in avg_thermal_sensation['cluster'].unique():
#     cluster_data = avg_thermal_sensation[avg_thermal_sensation['cluster'] == cluster]
#     plt.plot(cluster_data['ta'], cluster_data['thermal_sensation'], marker='o', label=f'Cluster {cluster}')
#
# plt.xlabel('Temperature (ta)')
# plt.ylabel('Average Thermal Sensation')
# plt.title('Average Thermal Sensation vs. Temperature by Cluster')
# plt.legend()
# plt.grid(True)
# plt.show()


# import pandas as pd
#
# # 加载数据
# data = pd.read_csv('knn/ashrae_comfort_data.csv')
#
# # 清理数据，移除缺失值
# data = data.dropna(subset=['season', 'climate', 'ta', 'thermal_sensation'])
#
# # 获取唯一的季节和气候组合
# season_climate_groups = data.groupby(['season', 'climate']).size().reset_index().drop(0, axis=1)
#
# # 创建一个存储目录
# import os
#
# output_dir = 'classified_data'
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
#
# # 按季节和气候分类数据并存储
# for index, row in season_climate_groups.iterrows():
#     season = row['season']
#     climate = row['climate']
#     subset = data[(data['season'] == season) & (data['climate'] == climate)]
#
#     # 创建子目录
#     dir_path = os.path.join(output_dir, season, climate)
#     if not os.path.exists(dir_path):
#         os.makedirs(dir_path)
#
#     # 保存数据
#     file_path = os.path.join(dir_path, 'data.csv')
#     subset.to_csv(file_path, index=False)





# def preprocess_data():
#     # 读取数据
#     df = pd.read_csv('./knn/raw_ashrae_db2.01.csv', low_memory=False)
#     df = df.dropna(subset=['Sex'])
#     # 计算 BMI 并添加到 DataFrame 中
#     df['BMI'] = df["Subject weight (kg)"] / ((df["Subject height (cm)"]) / 100 ** 2)
#     climate_mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
#     df['Climate'] = df['Koppen climate classification'].str[0].map(climate_mapping)
#     # 选择特征，包括 BMI 而不是 ht 和 wt
#     features = ['Season', 'Climate', 'Age', 'Sex', 'Air temperature (C)', 'Thermal sensation', 'BMI']
#
#     df['Season'] = df['Season'].map({'Spring': 0, 'Summer': 1, 'Autumn': 2, 'Winter': 3})
#     df['Sex'] = df['Sex'].map({'Male': 0, 'Female': 1})
#     # 去除缺失值数量大于 2 的行
#     df = df[df[features].isnull().sum(axis=1) <= 2]
#
#     print("缺失值情况:")
#     print(df[features].isna().sum())
#     print(len(df[features]))
#
#     imputer = KNNImputer(n_neighbors=5)
#     df[features] = imputer.fit_transform(df[features])
#
#     # 查看填补缺失值后的情况
#     print("填补缺失值后的情况:")
#     print(df[features].isna().sum())
#
#     df.to_csv('./knn/KNN_processed_raw_data.csv', index=False)
#
#
# preprocess_data()

import pandas as pd

# 加载数据
data = pd.read_csv('knn/KNN_processed_raw_data.csv')

# features = ['Season', 'Climate', 'Age', 'Sex', 'Air temperature (C)', 'Thermal sensation', 'BMI']

# 获取唯一的季节和气候组合
season_climate_groups = data.groupby(['Season', 'Climate']).size().reset_index().drop(columns=0)

# 创建一个存储目录
import os

output_dir = 'knn/classified_data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

climate_mapping = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
season_mapping = {0: 'Spring', 1: 'Summer', 2: 'Autumn', 3: 'Winter'}
# 按季节和气候分类数据并存储
for index, row in season_climate_groups.iterrows():
    season = row['Season']
    climate = row['Climate']
    subset = data[(data['Season'] == season) & (data['Climate'] == climate)]

    # 创建子目录
    dir_path = os.path.join(output_dir, season_mapping[season], climate_mapping[climate])
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # 保存数据
    file_path = os.path.join(dir_path, 'data.csv')
    subset.to_csv(file_path, index=False)
