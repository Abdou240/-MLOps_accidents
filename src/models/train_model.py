
import sklearn
import pandas as pd 
from sklearn import ensemble
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score


import joblib
import numpy as np

from mlflow import MlflowClient
import mlflow

print(joblib.__version__)

X_train = pd.read_csv('data/preprocessed/X_train.csv')
X_test = pd.read_csv('data/preprocessed/X_test.csv')
y_train = pd.read_csv('data/preprocessed/y_train.csv')
y_test = pd.read_csv('data/preprocessed/y_test.csv')
y_train = np.ravel(y_train)
y_test = np.ravel(y_test)



# Train model
params = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42,
    "n_jobs": -1,
}

rf_classifier = ensemble.RandomForestClassifier(**params)

#--Train the model
rf_classifier.fit(X_train, y_train)

#--Save the trained model to a file
model_filename = './src/models/trained_model.joblib'
joblib.dump(rf_classifier, model_filename)
print("Model trained and saved successfully.")

# Evaluate model
y_pred = rf_classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
metrics = {"accuracy": accuracy, 
           "precision": precision, 
           "recall": recall, 
           "f1": f1}
print(metrics)



# Define tracking_uri
client = MlflowClient(tracking_uri="http://127.0.0.1:9090")

# Define experiment name, run name and artifact_path name
car_accidents_experiment = mlflow.set_experiment("car_accidents")
run_name = "second_run"
artifact_path = "rf_car_accidents"

# Store information in tracking server
with mlflow.start_run(run_name=run_name) as run:
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(
        sk_model=rf_classifier, input_example=X_test, artifact_path=artifact_path)