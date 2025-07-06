import mlflow
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression

X, y = make_regression(n_samples=100, n_features=1, noise=0.1)
model = LinearRegression().fit(X, y)

with mlflow.start_run() as run:
    mlflow.sklearn.log_model(model, "model")
    print("Run ID:", run.info.run_id)