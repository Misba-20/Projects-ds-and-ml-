# 1. Import Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# 2. Import Dataset
data = pd.read_csv("Salary_Data.csv")

print("First 5 Rows of Dataset:")
print(data.head())

print("\nDataset Information:")
print(data.info())

print("\nMissing Values:")
print(data.isnull().sum())

# 3. Data Cleaning & Preprocessing
data = data.dropna()

X = data[['YearsExperience']]   # Feature
y = data['Salary']              # Target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Simple Linear Regression using Sklearn
sk_model = LinearRegression()
sk_model.fit(X_train, y_train)

y_pred_sklearn = sk_model.predict(X_test)

mse_sklearn = mean_squared_error(y_test, y_pred_sklearn)
print("\nSklearn Mean Squared Error:", mse_sklearn)

# 5. Simple Linear Regression WITHOUT Sklearn (Manual)
x_train = X_train.values.flatten()
y_train_manual = y_train.values
n = len(x_train)

m = (n * np.sum(x_train * y_train_manual) - np.sum(x_train) * np.sum(y_train_manual)) / \
    (n * np.sum(x_train ** 2) - (np.sum(x_train)) ** 2)

c = (np.sum(y_train_manual) - m * np.sum(x_train)) / n

print("\nManual Slope (m):", m)
print("Manual Intercept (c):", c)

x_test = X_test.values.flatten()
y_pred_manual = m * x_test + c

mse_manual = np.mean((y_test.values - y_pred_manual) ** 2)
print("Manual Mean Squared Error:", mse_manual)

# 6. Compare Results
results = pd.DataFrame({
    'YearsExperience': x_test,
    'Actual Salary': y_test.values,
    'Sklearn Prediction': y_pred_sklearn,
    'Manual Prediction': y_pred_manual
})

print("\nComparison of Predictions:")
print(results.head())

# 7. Visualization
plt.figure()
plt.scatter(X, y)
plt.plot(X_test, y_pred_sklearn)
plt.xlabel("Years of Experience")
plt.ylabel("Salary")
plt.title("Simple Linear Regression using Sklearn")
plt.show()

plt.figure()
plt.scatter(X, y)
plt.plot(x_test, y_pred_manual)
plt.xlabel("Years of Experience")
plt.ylabel("Salary")
plt.title("Simple Linear Regression (Manual Implementation)")
plt.show()

# 8. Export Results
results.to_csv("Salary_Predictions.csv", index=False)
print("\nResults saved as 'Salary_Predictions.csv'")




