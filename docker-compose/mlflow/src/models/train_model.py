
import sklearn
import pandas as pd 
from sklearn import ensemble
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
import requests

import joblib
import numpy as np

from mlflow import MlflowClient
import mlflow
import pandas as pd
import json
from sklearn.model_selection import train_test_split
#print(joblib.__version__)

def read_data_from_csv():
    base = '../../'
    X_train = pd.read_csv(base+'data/preprocessed/X_train.csv')
    X_test = pd.read_csv(base+'data/preprocessed/X_test.csv')
    y_train = pd.read_csv(base+'data/preprocessed/y_train.csv')
    y_test = pd.read_csv(base+'data/preprocessed/y_test.csv')
    y_train = np.ravel(y_train)
    y_test = np.ravel(y_test)
    return X_train, X_test, y_train, y_test

def read_data_from_database():
    # "catu": 3,
    # "victim_age" : 60,
    # "lum" : 5,
    # "com" : 77317,
    # "atm" : 0
    gen_query = 'SELECT catu, victim_age, lum, com, atm, grav FROM dataset;'
    res = requests.post('http://database:9090/data', json={'query': gen_query})
    res = res.json()
    #print(res)
    df = pd.read_json(json.dumps(res, indent=2))

    target = df['grav']
    print('counts', df.grav.value_counts())
    feats = df.drop(['grav'], axis = 1)
    
    X_train, X_test, y_train, y_test = train_test_split(feats, target, test_size=0.3, random_state = 42)
    y_train = np.ravel(y_train)
    y_test = np.ravel(y_test)
    return X_train, X_test, y_train, y_test




def train_model(in_params:dict={}):
    X_train, X_test, y_train, y_test =  read_data_from_database()

    params = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42,
    "n_jobs": -1,
    }

    for k in in_params:
        params[k]=in_params[k]

    estimators = params["n_estimators"]
    depth = params["max_depth"]

    # Train model
    rf_classifier = ensemble.RandomForestClassifier(**params)

    #--Train the model
    rf_classifier.fit(X_train, y_train)

    #--Save the trained model to a file
    model_filename = f'./src/models/trained_model_{estimators}_estimators_{depth}_depth.joblib'
    #joblib.dump(rf_classifier, model_filename)
    print("Model trained and saved successfully.")

    # Evaluate model
    y_pred = rf_classifier.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    metrics = {"accuracy": accuracy, 
            "precision": precision, 
            "recall": recall, 
            "f1": f1}
    print(metrics)


    # Define tracking_uri
    client = MlflowClient(tracking_uri="http://0.0.0.0:8000")

    # Define experiment name, run name and artifact_path name
    car_accidents_experiment = mlflow.set_experiment("car_accidents")
    run_name = f"run_with_{estimators}_estimators_{depth}_depth"
    artifact_path = "rf_car_accidents"

    # Store information in tracking server
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            sk_model=rf_classifier, input_example=X_test, artifact_path=artifact_path)
    return run_name

if __name__ == '__main__':
    x = read_data_from_csv()
    for i in x:
        print(i.shape)
    x = read_data_from_database()
    for i in x:
        print(i.shape)
