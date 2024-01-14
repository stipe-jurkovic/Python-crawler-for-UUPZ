import pandas as pd
import joblib
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
import os

# Construct the absolute path to the 'merged_data_filtered.csv' file
# file_path = os.path.join(os.pardir, "data", "merged_data_filtered.csv")
file_path = os.path.join(os.pardir, "data", "csvovi", "dubrovacko-neretvanska", "dubrovacko-neretvanskacleaned.csv")

# Load the data
df = pd.read_csv(file_path)

# Features and target variable
X = df.drop(['url', 'linenum', 'price'], axis=1)
y = df['price']

# One-hot encode categorical variables
X_encoded = pd.get_dummies(X)

# Use Min-Max scaling
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X_encoded)

scaled_df = pd.DataFrame(X_scaled, columns=X_encoded.columns)

# Save the scaled DataFrame to a CSV file
scaled_csv_path = os.path.join(os.pardir, "data", "scaled_data.csv")
scaled_df.to_csv(scaled_csv_path, index=False)
print(f"Scaled data saved as {scaled_csv_path}")

# Initialize the model
model = MLPRegressor(hidden_layer_sizes=(20, 20), max_iter=1000, activation='relu')

# Cross-validation parameters
cv_folds = 5
scoring_metric = 'neg_mean_squared_error'

# Use cross-validation to evaluate the model
cv_scores = cross_val_score(model, X_scaled, y, cv=cv_folds, scoring=scoring_metric)

# Display cross-validation scores
print("Cross-Validation Scores:")
print(-cv_scores)

# Calculate mean squared error from cross-validation scores
mean_mse = -cv_scores.mean()
print(f'Mean Squared Error: {mean_mse:.4f}')

# Train the model on the entire dataset
model.fit(X_scaled, y)

# Save the trained model to a file inside the "data" folder
model_filename = os.path.join(os.pardir, "data", "trained_model.joblib")
joblib.dump(model, model_filename)
print(f"Model saved as {model_filename}")

# Load the trained model from the file
loaded_model = joblib.load(model_filename)
print("Model loaded from file")
