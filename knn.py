# Import necessary libraries
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer

import matplotlib.pyplot as plt
import joblib


def knn_train(params):

    # Load your dataset
    data = pd.read_csv('knn/ashrae_comfort_data.csv',  low_memory=False)

    data.dropna(subset=['thermal_sensation'], inplace=True)
    # Split the dataset into features (X) and target variable (y)
    X = data[params]
    y = data['thermal_sensation']

    # Convert categorical variables ('gender') to numerical using one-hot encoding
    # X = pd.get_dummies(X, columns=['gender'], drop_first=True)
    #
    # # Ensure that 'gender_undefined' column is present in the features with 0 values if not applicable
    # if 'gender_undefined' not in X.columns:
    #     X['gender_undefined'] = 0

    # Impute missing values in 'age' and 'ta' columns with the mean
    X = X.copy(deep=True)
    imputer = SimpleImputer(strategy='mean')
    X.loc[:, params] = imputer.fit_transform(X[params])

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)


    # Create a K-Nearest Neighbors Regressor model (you can adjust the number of neighbors)
    knn_model = KNeighborsRegressor(n_neighbors=20)

    # Fit the model to the training data
    knn_model.fit(X_train, y_train)

    # Make predictions on the test data
    y_pred = knn_model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)


    print(f"Mean Squared Error: {mse:.2f}")
    print(f"R-squared (R2) Score: {r2:.2f}")

    return knn_model
    # joblib.dump(knn_model, 'knn_model.pkl')


# if __name__ == '__main__':
#     knn_train(['age', 'gender', 'activity_10', 'weight_level', 'ta'])

# Now, you can use the model to make predictions for new data points
# For example, to predict thermal comfort for a new data point:
# new_data_point = pd.DataFrame({'age': [30], 'ta': [25]})  # Replace with your own data
# new_data_point[['age', 'ta']] = imputer.transform(new_data_point[['age', 'ta']])
# #
# # Ensure that 'gender_undefined' column is present in the new data point with 0 value if not applicable
# # if 'gender_undefined' not in new_data_point.columns:
# #     new_data_point['gender_undefined'] = 0
#
# predicted_comfort = knn_model.predict(new_data_point)
#
# print(f"Predicted Thermal Comfort: {predicted_comfort[0]:.2f}")