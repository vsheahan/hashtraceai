import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Create some dummy data
np.random.seed(42)
X = np.random.randn(100, 5)
y = X[:, 0] + 2 * X[:, 1] - X[:, 2] + 0.5 * np.random.randn(100)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a simple model
model = LinearRegression()
model.fit(X_train, y_train)

# Log the model with MLflow
with mlflow.start_run():
    mlflow.sklearn.log_model(
        model, "linear_regression_model", registered_model_name="TestLinearRegression"
    )

    # Log some metrics and parameters
    mlflow.log_param("n_features", X.shape[1])
    mlflow.log_metric("train_score", model.score(X_train, y_train))
    mlflow.log_metric("test_score", model.score(X_test, y_test))

    print("Model logged successfully!")
    print(f"MLflow tracking URI: {mlflow.get_tracking_uri()}")
    print(f"Run ID: {mlflow.active_run().info.run_id}")
