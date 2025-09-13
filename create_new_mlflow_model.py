import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import os

# Set MLflow tracking URI to local directory
mlflow.set_tracking_uri("file:./mlruns")

print("Creating a new Random Forest model...")

# Create classification dataset
X, y = make_classification(
    n_samples=1000,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    n_classes=3,
    random_state=42,
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Log the model with MLflow
with mlflow.start_run() as run:
    # Log parameters
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("n_features", X.shape[1])
    mlflow.log_param("n_samples", X.shape[0])

    # Log metrics
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    mlflow.log_metric("train_accuracy", train_score)
    mlflow.log_metric("test_accuracy", test_score)

    # Log the model
    mlflow.sklearn.log_model(
        model, "random_forest_model", registered_model_name="HashTraceTestRandomForest"
    )

    # Create some additional artifacts
    feature_importance = model.feature_importances_
    np.save("feature_importance.npy", feature_importance)
    mlflow.log_artifact("feature_importance.npy")

    print("✅ Model logged successfully!")
    print(f"📁 Run ID: {run.info.run_id}")
    print(f"📊 Train Accuracy: {train_score:.3f}")
    print(f"📊 Test Accuracy: {test_score:.3f}")
    print(
        f"📂 Model artifacts saved to: mlruns/0/{run.info.run_id}/artifacts/random_forest_model"
    )

    # Clean up temporary file
    if os.path.exists("feature_importance.npy"):
        os.remove("feature_importance.npy")
