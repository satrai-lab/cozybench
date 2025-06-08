import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer


def knn_train(params):

    # Load your dataset
    data = pd.read_csv('knn/ashrae_comfort_data.csv',  low_memory=False)

    data.dropna(subset=['thermal_sensation'], inplace=True)
    # Split the dataset into features (X) and target variable (y)
    X = data[params]
    y = data['thermal_sensation']

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


    # print(f"Mean Squared Error: {mse:.2f}")
    # print(f"R-squared (R2) Score: {r2:.2f}")

    return knn_model
