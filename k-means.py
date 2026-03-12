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
#     # Read the data
#     df = pd.read_csv('./knn/ashrae_comfort_data.csv', low_memory=False)
#
#     # Compute BMI and add it to the DataFrame
#     df['BMI'] = df['wt'] / ((df['ht']) ** 2)
#
#     # Select features, using BMI instead of ht and wt
#     features = ['season', 'age', 'gender', 'ta', 'thermal_sensation', 'BMI']
#
#     df['season'] = df['season'].map({'winter': 0, 'summer': 1})
#
#     # Remove rows with too many missing values
#     df = df[df[features].isnull().sum(axis=1) <= 1]
#
#     print("Missing values:")
#     print(df[features].isna().sum())
#
#     imputer = KNNImputer(n_neighbors=5)
#     df[features] = imputer.fit_transform(df[features])
#
#     # Inspect missing values after imputation
#     print("Missing values after imputation:")
#     print(df[features].isna().sum())
#
#     df[features].to_csv('./knn/KNN_processed_ashrae_comfort_data.csv', index=False)
#
#
# # preprocess_data()
#
# # Read the processed dataset
# df = pd.read_csv('knn/KNN_processed_ashrae_comfort_data.csv')
#
# # Ensure column names are consistent
# features = ['season', 'age', 'gender', 'ta', 'thermal_sensation', 'BMI']
#
# X = df[features]
#
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)
#
# # Use the elbow method to determine the optimal K value
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
# optimal_k = 5  # Choose the optimal K value based on the elbow method
# kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
# df['cluster'] = kmeans.fit_predict(X_scaled)
#
# # Inspect clustering results
# print(df['cluster'].value_counts())
#
# # Save clustering results
# df.to_csv('clustered_ashrae_comfort_data.csv', index=False)
#
# # Compute the average thermal sensation for each ta value within each cluster
# avg_thermal_sensation = df.groupby(['cluster', 'ta'])['thermal_sensation'].mean().reset_index()
#
# # Plot the chart
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
# # Load data
# data = pd.read_csv('knn/ashrae_comfort_data.csv')
#
# # Clean the data and remove missing values
# data = data.dropna(subset=['season', 'climate', 'ta', 'thermal_sensation'])
#
# # Get unique season-climate combinations
# season_climate_groups = data.groupby(['season', 'climate']).size().reset_index().drop(0, axis=1)
#
# # Create an output directory
# import os
#
# output_dir = 'classified_data'
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
#
# # Split the data by season and climate and save it
# for index, row in season_climate_groups.iterrows():
#     season = row['season']
#     climate = row['climate']
#     subset = data[(data['season'] == season) & (data['climate'] == climate)]
#
#     # Create a subdirectory
#     dir_path = os.path.join(output_dir, season, climate)
#     if not os.path.exists(dir_path):
#         os.makedirs(dir_path)
#
#     # Save the data
#     file_path = os.path.join(dir_path, 'data.csv')
#     subset.to_csv(file_path, index=False)





# def preprocess_data():
#     # Read the data
#     df = pd.read_csv('./knn/raw_ashrae_db2.01.csv', low_memory=False)
#     df = df.dropna(subset=['Sex'])
#     # Compute BMI and add it to the DataFrame
#     df['BMI'] = df["Subject weight (kg)"] / ((df["Subject height (cm)"]) / 100 ** 2)
#     climate_mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
#     df['Climate'] = df['Koppen climate classification'].str[0].map(climate_mapping)
#     # Select features, using BMI instead of ht and wt
#     features = ['Season', 'Climate', 'Age', 'Sex', 'Air temperature (C)', 'Thermal sensation', 'BMI']
#
#     df['Season'] = df['Season'].map({'Spring': 0, 'Summer': 1, 'Autumn': 2, 'Winter': 3})
#     df['Sex'] = df['Sex'].map({'Male': 0, 'Female': 1})
#     # Remove rows with too many missing values
#     df = df[df[features].isnull().sum(axis=1) <= 2]
#
#     print("Missing values:")
#     print(df[features].isna().sum())
#     print(len(df[features]))
#
#     imputer = KNNImputer(n_neighbors=5)
#     df[features] = imputer.fit_transform(df[features])
#
#     # Inspect missing values after imputation
#     print("Missing values after imputation:")
#     print(df[features].isna().sum())
#
#     df.to_csv('./knn/KNN_processed_raw_data.csv', index=False)
#
#
# preprocess_data()

import pandas as pd

# Load data
data = pd.read_csv('knn/KNN_processed_raw_data.csv')

# features = ['Season', 'Climate', 'Age', 'Sex', 'Air temperature (C)', 'Thermal sensation', 'BMI']

# Get unique season-climate combinations
season_climate_groups = data.groupby(['Season', 'Climate']).size().reset_index().drop(columns=0)

# Create an output directory
import os

output_dir = 'knn/classified_data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

climate_mapping = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
season_mapping = {0: 'Spring', 1: 'Summer', 2: 'Autumn', 3: 'Winter'}
# Split the data by season and climate and save it
for index, row in season_climate_groups.iterrows():
    season = row['Season']
    climate = row['Climate']
    subset = data[(data['Season'] == season) & (data['Climate'] == climate)]

    # Create a subdirectory
    dir_path = os.path.join(output_dir, season_mapping[season], climate_mapping[climate])
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # Save the data
    file_path = os.path.join(dir_path, 'data.csv')
    subset.to_csv(file_path, index=False)
